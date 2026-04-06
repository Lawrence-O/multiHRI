"""
Generate HDF5 datasets from trained Overcooked agents.
One .h5 file per layout, written to an output directory.

Schema (per file):
    /
        obs              (E, T+1, N, H, W, C)  int16   all-agent egocentric obs
        actions          (E, T,   N, 1)         int64   action indices 0-5
        sparse_rewards   (E, T,   N, 1)         float64 per-agent sparse reward
        shaped_rewards   (E, T,   N, 1)         float64 per-agent shaped reward
        dones            (E, T,   N)            bool    (same for all agents)
        policy_id        (E, N)                 bytes   e.g. "mHRI_3_chef_SP_s13"
        env_info/
            ep_sparse_r          (E,)    float64  sum sparse all agents all steps
            ep_shaped_r          (E,)    float64  sum shaped all agents all steps
            ep_length            (E,)    int64    actual episode length
            ep_sparse_r_by_agent (E, N)  float64  per-agent total sparse
            ep_shaped_r_by_agent (E, N)  float64  per-agent total shaped

Usage:
    # Single checkpoint → datasets/3chef_sp/<layout>.h5
    python scripts/generate_hdf5_dataset.py \\
        --checkpoint agent_models/Complex/3/SP_s13_h256_tr[SP]_ran/best \\
        --episodes 50 --output-dir datasets/3chef_sp

    # All seeds under a parent dir
    python scripts/generate_hdf5_dataset.py \\
        --parent-dir agent_models/Complex/3 \\
        --episodes 25 --output-dir datasets/3chef_sp_all_seeds
"""

import argparse
import copy
import json
import logging
import sys
import time
from pathlib import Path

import h5py
import numpy as np
import torch as th

from overcooked_ai_py.mdp.overcooked_mdp import Action

# Unbuffered stream logger so output appears immediately under conda run
log = logging.getLogger("gen_dataset")
log.setLevel(logging.INFO)
_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(logging.Formatter("%(asctime)s  %(message)s", datefmt="%H:%M:%S"))
log.addHandler(_handler)

from oai_agents.agents.agent_utils import load_agent
from oai_agents.common.state_encodings import ENCODING_SCHEMES
from oai_agents.gym_environments.base_overcooked_env import OvercookedGymEnv


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(description="Generate HDF5 dataset from trained agents")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--checkpoint", type=str,
                       help="Path to a single agent checkpoint dir (e.g. .../best)")
    group.add_argument("--parent-dir", type=str,
                       help="Parent dir with multiple SP_s*_h*/best checkpoints")

    parser.add_argument("--ck-name", type=str, default="best",
                        help="Checkpoint subfolder name (default: best)")
    parser.add_argument("--episodes", type=int, default=50,
                        help="Episodes per layout per checkpoint")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Output directory for per-layout .h5 files (default: datasets/<stem>_<ck>)")
    parser.add_argument("--horizon", type=int, default=400,
                        help="Episode horizon (default: 400)")
    parser.add_argument("--layouts", type=str, nargs="*", default=None,
                        help="Override layout list (default: agent's training layouts)")
    parser.add_argument("--deterministic", action="store_true",
                        help="Deterministic actions (default: stochastic)")
    parser.add_argument("--full-obs", action="store_true",
                        help="Store full-map lossless obs (W,H,27) instead of 7x7 egocentric crop")
    parser.add_argument("--policy-id", type=str, default=None,
                        help="Override policy_id tag (default: auto from checkpoint)")
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Checkpoint discovery / loading
# ---------------------------------------------------------------------------
def discover_checkpoints(parent_dir: str, ck_name: str) -> list:
    parent = Path(parent_dir)
    ckpts = sorted([d / ck_name for d in parent.iterdir()
                    if d.is_dir() and d.name.startswith("SP_") and (d / ck_name).exists()])
    return ckpts


def load_agent_and_args(ckpt_path: str):
    ckpt_path = Path(ckpt_path)
    agent_file = ckpt_path / "agents_dir" / "agent_0" / "agent_file"
    if not agent_file.exists():
        agent_file = ckpt_path / "agent_file"

    saved = th.load(agent_file, map_location="cpu", weights_only=False)
    args = copy.deepcopy(saved["const_params"]["args"])
    args.device = th.device("cuda" if th.cuda.is_available() else "cpu")
    agent = load_agent(ckpt_path, args)
    return agent, args


def make_policy_id(args, ckpt_path: Path, override) -> str:
    """Derive a human-readable policy id string."""
    if override:
        return override
    n = getattr(args, "num_players", 2)
    seed_dir = ckpt_path.parent.name  # e.g. SP_s13_h256_tr[SP]_ran
    return f"mHRI_{n}_chef_{seed_dir}"


# ---------------------------------------------------------------------------
# Episode collection  (bypasses OvercookedSimulation for full control)
# ---------------------------------------------------------------------------
def collect_layout_episodes(
    agent, args, layout_name: str, num_episodes: int,
    horizon: int, deterministic: bool, policy_id_str: str,
    full_obs: bool = False,
):
    """
    Run *num_episodes* on *layout_name* and return pre-allocated numpy arrays
    matching the target HDF5 schema.
    """
    num_players = getattr(args, "num_players", 2)
    encoding_fn = ENCODING_SCHEMES[getattr(args, "encoding_fn", "OAI_egocentric")]
    grid_shape = (7, 7) if args.encoding_fn == "OAI_egocentric" else None

    # --- Create env --------------------------------------------------------
    env = OvercookedGymEnv(
        args=args,
        layout_name=layout_name,
        ret_completed_subtasks=False,
        is_eval_env=True,
        horizon=horizon,
        learner_type="originaler",
    )
    teammates = [agent] * (num_players - 1)
    env.set_teammates(teammates)

    # Full-obs: use raw lossless encoding (full W x H x 27 grid per player)
    if full_obs:
        def _full_obs_encode(mdp, state, _grid_shape, _horizon, p_idx=None, goal_objects=None):
            raw = mdp.lossless_state_encoding(state, horizon=_horizon, goal_objects=goal_objects, p_idx=p_idx)
            if p_idx is not None:
                vis = np.transpose(raw, (2, 0, 1))[np.newaxis]  # (1, C, W, H)
            else:
                vis = np.stack(raw, axis=0)                      # (N, W, H, C)
                vis = np.transpose(vis, (0, 3, 1, 2))            # (N, C, W, H)
            return {"visual_obs": vis}
        obs_encoding_fn = _full_obs_encode
        obs_grid_shape = None
    else:
        obs_encoding_fn = encoding_fn
        obs_grid_shape = grid_shape

    # Figure out obs shape from a probe encoding
    probe = obs_encoding_fn(env.mdp, env.state, obs_grid_shape, horizon, p_idx=None)
    vis = probe["visual_obs"]                         # (N, C, H, W)
    N, C, H, W = vis.shape
    assert N == num_players

    # --- Pre-allocate arrays -----------------------------------------------
    T = horizon
    all_obs       = np.zeros((num_episodes, T + 1, N, H, W, C), dtype=np.int16)
    all_actions   = np.zeros((num_episodes, T, N, 1),            dtype=np.int64)
    all_sparse_r  = np.zeros((num_episodes, T, N, 1),            dtype=np.float64)
    all_shaped_r  = np.zeros((num_episodes, T, N, 1),            dtype=np.float64)
    all_dones     = np.zeros((num_episodes, T, N),               dtype=bool)

    ep_sparse_r          = np.zeros(num_episodes,           dtype=np.float64)
    ep_shaped_r          = np.zeros(num_episodes,           dtype=np.float64)
    ep_length            = np.zeros(num_episodes,           dtype=np.int64)
    ep_sparse_r_by_agent = np.zeros((num_episodes, N),      dtype=np.float64)
    ep_shaped_r_by_agent = np.zeros((num_episodes, N),      dtype=np.float64)

    # --- Set encoding params for agent & teammates -------------------------
    def _setup_agents(p_idx):
        env.reset(p_idx=p_idx)
        agent.set_encoding_params(p_idx, horizon, env=env, is_haha=False, tune_subtasks=False)
        env.encoding_fn = agent.encoding_fn
        for t_idx, tm in enumerate(env.teammates):
            tm.set_encoding_params(t_idx + 1, horizon, env=env, is_haha=False, tune_subtasks=True)
        env.deterministic = deterministic

    # --- Run episodes ------------------------------------------------------
    ep_t0 = time.time()
    for ep in range(num_episodes):
        p_idx = ep % num_players  # rotate ego position
        _setup_agents(p_idx)
        env.reset(p_idx=p_idx)

        # Initial obs for ALL agents  (N, C, H, W) → (N, H, W, C)
        obs0 = obs_encoding_fn(env.mdp, env.state, obs_grid_shape, horizon, p_idx=None)["visual_obs"]
        all_obs[ep, 0] = np.transpose(obs0, (0, 2, 3, 1))

        done = False
        for t in range(T):
            if done:
                # Pad remainder with last obs / zeros (episode already ended)
                all_obs[ep, t + 1] = all_obs[ep, t]
                all_dones[ep, t] = True
                continue

            # Ego action
            ego_obs = env.get_obs(env.p_idx)
            action = agent.predict(ego_obs, state=env.state, deterministic=deterministic)[0]

            # Step (handles teammate predictions internally)
            _, _, done, info = env.step(action)

            # Joint action → index per agent
            joint_action = env.get_joint_action()          # list of tuples / 'interact'
            for i, a in enumerate(joint_action):
                all_actions[ep, t, i, 0] = Action.ACTION_TO_INDEX[a]

            # Per-agent rewards
            sparse_r = np.array(info["sparse_r_by_agent"], dtype=np.float64)
            shaped_r = np.array(info["shaped_r_by_agent"], dtype=np.float64)
            all_sparse_r[ep, t, :, 0] = sparse_r
            all_shaped_r[ep, t, :, 0] = shaped_r

            # Done flag (same for all agents)
            all_dones[ep, t, :] = done

            # Next obs for ALL agents
            obs_t = obs_encoding_fn(env.mdp, env.state, obs_grid_shape, horizon, p_idx=None)["visual_obs"]
            all_obs[ep, t + 1] = np.transpose(obs_t, (0, 2, 3, 1))

            # Accumulate episode stats
            ep_sparse_r_by_agent[ep] += sparse_r
            ep_shaped_r_by_agent[ep] += shaped_r

        ep_sparse_r[ep] = ep_sparse_r_by_agent[ep].sum()
        ep_shaped_r[ep] = ep_shaped_r_by_agent[ep].sum()
        ep_length[ep] = T  # always runs full horizon

        # Log every 10 episodes or on the last one
        if (ep + 1) % 10 == 0 or ep == num_episodes - 1:
            elapsed = time.time() - ep_t0
            eps_per_sec = (ep + 1) / elapsed
            eta = (num_episodes - ep - 1) / eps_per_sec if eps_per_sec > 0 else 0
            log.info("      ep %d/%d  sparse=%.1f  (%.1f ep/s, ETA %.0fs)",
                     ep + 1, num_episodes, ep_sparse_r[ep], eps_per_sec, eta)

    # --- Build policy_id array ---------------------------------------------
    policy_id = np.full((num_episodes, N), policy_id_str.encode("utf-8"))

    return {
        "obs": all_obs,
        "actions": all_actions,
        "sparse_rewards": all_sparse_r,
        "shaped_rewards": all_shaped_r,
        "dones": all_dones,
        "policy_id": policy_id,
        "env_info": {
            "ep_sparse_r": ep_sparse_r,
            "ep_shaped_r": ep_shaped_r,
            "ep_length": ep_length,
            "ep_sparse_r_by_agent": ep_sparse_r_by_agent,
            "ep_shaped_r_by_agent": ep_shaped_r_by_agent,
        },
    }


# ---------------------------------------------------------------------------
# HDF5 writing
# ---------------------------------------------------------------------------
def write_layout_file(out_dir: Path, layout_name: str, data: dict, metadata: dict):
    """Write (or append to) a per-layout HDF5 file."""
    fpath = out_dir / f"{layout_name}.h5"
    mode = "a" if fpath.exists() else "w"

    with h5py.File(fpath, mode) as hf:
        # Write / update metadata attrs
        for k, v in metadata.items():
            hf.attrs[k] = v

        if "obs" in hf:
            # Append along episode axis (axis 0)
            for key in ("obs", "actions", "sparse_rewards", "shaped_rewards", "dones", "policy_id"):
                old = hf[key]
                new = data[key]
                old.resize(old.shape[0] + new.shape[0], axis=0)
                old[-new.shape[0]:] = new
            ei = hf["env_info"]
            for key in data["env_info"]:
                old = ei[key]
                new = data["env_info"][key]
                old.resize(old.shape[0] + new.shape[0], axis=0)
                old[-new.shape[0]:] = new
        else:
            for key in ("obs", "actions", "sparse_rewards", "shaped_rewards", "dones", "policy_id"):
                arr = data[key]
                maxshape = (None,) + arr.shape[1:]   # resizable on episode dim
                compress = {"compression": "gzip", "compression_opts": 4} if key == "obs" else {}
                hf.create_dataset(key, data=arr, maxshape=maxshape, chunks=True, **compress)
            ei_grp = hf.create_group("env_info")
            for key, arr in data["env_info"].items():
                maxshape = (None,) + arr.shape[1:]
                ei_grp.create_dataset(key, data=arr, maxshape=maxshape, chunks=True)

    return fpath


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    cli = parse_args()

    # Discover checkpoints
    ckpt_paths = ([Path(cli.checkpoint)] if cli.checkpoint
                  else discover_checkpoints(cli.parent_dir, cli.ck_name))
    if not ckpt_paths:
        log.error("No checkpoints found!")
        return

    log.info("Found %d checkpoint(s):", len(ckpt_paths))
    for p in ckpt_paths:
        log.info("  %s", p)

    # Output directory (one .h5 per layout)
    if cli.output_dir:
        out_dir = Path(cli.output_dir)
    else:
        stem = (Path(cli.checkpoint).parent.name if cli.checkpoint
                else Path(cli.parent_dir).name)
        out_dir = Path("datasets") / f"{stem}_{cli.ck_name}"
    out_dir.mkdir(parents=True, exist_ok=True)

    log.info("Output dir: %s/", out_dir)
    log.info("Episodes per layout per ckpt: %d", cli.episodes)
    log.info("Horizon: %d  Deterministic: %s  Full-obs: %s", cli.horizon, cli.deterministic, cli.full_obs)

    # Shared metadata written into every file
    file_meta = {
        "horizon": cli.horizon,
        "deterministic": cli.deterministic,
        "episodes_per_layout_per_ckpt": cli.episodes,
        "num_checkpoints": len(ckpt_paths),
        "checkpoint_paths": json.dumps([str(p) for p in ckpt_paths]),
    }

    total_eps = 0
    total_mb = 0.0
    t0 = time.time()

    for ci, ckpt_path in enumerate(ckpt_paths):
        log.info("[%d/%d] Loading %s ...", ci + 1, len(ckpt_paths), ckpt_path)
        agent, args = load_agent_and_args(str(ckpt_path))

        layouts = cli.layouts or args.layout_names
        num_players = getattr(args, "num_players", 2)
        pid = make_policy_id(args, ckpt_path, cli.policy_id)

        log.info("  num_players=%d, layouts=%d, policy_id=%s", num_players, len(layouts), pid)

        for li, layout_name in enumerate(layouts):
            lt0 = time.time()
            log.info("  [%d/%d] %s  (%d eps) ...", li + 1, len(layouts), layout_name, cli.episodes)

            try:
                data = collect_layout_episodes(
                    agent=agent, args=args,
                    layout_name=layout_name,
                    num_episodes=cli.episodes,
                    horizon=cli.horizon,
                    deterministic=cli.deterministic,
                    policy_id_str=pid,
                    full_obs=cli.full_obs,
                )
            except Exception as e:
                log.error("    FAILED: %s", e, exc_info=True)
                continue

            fpath = write_layout_file(out_dir, layout_name, data, file_meta)
            total_eps += data["obs"].shape[0]
            total_mb += fpath.stat().st_size / (1024 * 1024)

            avg_sp = data["env_info"]["ep_sparse_r"].mean()
            avg_sh = data["env_info"]["ep_shaped_r"].mean()
            dt = time.time() - lt0
            log.info("    done  %.1fs  sparse=%.1f  shaped=%.1f  [%.1f MB total]", dt, avg_sp, avg_sh, total_mb)

    elapsed = time.time() - t0
    n_files = len(list(out_dir.glob("*.h5")))
    log.info("Done! %d episodes across %d files | %s/ (%.1f MB) | %.1fs", total_eps, n_files, out_dir, total_mb, elapsed)


if __name__ == "__main__":
    main()
