"""Evaluate replacement policies with DiZCo's fixed SP teammates and seeds."""
from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import json
import math
import multiprocessing
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SEEDS = {"sp": (13, 68, 1010, 2020, 2602),
         "fcp": (13, 68, 1010, 2020, 2602),
         "mep": (1010, 2020, 2602, 13)}
CANONICAL = {3: 1010, 5: 13}
REFERENCE = Path(__file__).with_name("nagent_fixed_sp_reference.json")


def resolve_agent(best):
    for candidate in (best / "agents_dir" / "agent_0", best):
        if (candidate / "agent_file").is_file() and (
                candidate / "agent_file_sb3_agent.zip").is_file():
            return candidate.resolve()
    raise FileNotFoundError(f"missing policy checkpoint beneath {best}")


def policy_files(path):
    return {name: hashlib.sha256((path / name).read_bytes()).hexdigest()
            for name in ("agent_file", "agent_file_sb3_agent.zip")}


def policies(root, players, method):
    team = resolve_agent(
        root / "agent_models" / "HyakComplex" / str(players)
        / f"SP_s{CANONICAL[players]}_h256_tr[SP]_ran" / "best")
    result = []
    for seed in SEEDS[method]:
        if method == "sp" and seed == CANONICAL[players]:
            path = team
        else:
            dirname = (f"FCP_s{seed}_h256_tr[AMX]_ran" if method == "fcp"
                       else f"SP_s{seed}_h256_tr[SP]_ran")
            subdir = f"{players}_MEP" if method == "mep" else str(players)
            candidates = [root / "agent_models" / family / subdir / dirname / "best"
                          for family in ("Complex", "HyakComplex")]
            path = next((resolve_agent(best) for best in candidates
                         if best.is_dir()), None)
            if path is None:
                raise FileNotFoundError(f"missing {method} seed {seed}: {candidates}")
        result.append({"ego_seed": seed, "ego_path": str(path),
                       "ego_hashes": policy_files(path), "team_path": str(team),
                       "team_hashes": policy_files(team)})
    return sorted(result, key=lambda p: p["ego_path"] != str(team))


def atomic_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def run_episode(task):
    path = Path(task["episode_path"])
    semantic = {k: task[k] for k in (
        "players", "layout", "method", "ego_seed", "ego_hashes", "team_hashes",
        "episode", "seed", "max_steps", "execution_revision",
        "multihri_overcooked_src", "multihri_revision")}
    signature = hashlib.sha256(json.dumps(semantic, sort_keys=True).encode()).hexdigest()
    if path.exists():
        old = json.loads(path.read_text())
        if old.get("signature") != signature:
            raise ValueError(f"incompatible saved episode: {path}")
        return old
    import torch
    torch.set_num_threads(1)
    overcooked_src = Path(task["multihri_overcooked_src"]).resolve()
    if not (overcooked_src / "overcooked_ai_py" / "mdp" / "overcooked_mdp.py").is_file():
        raise FileNotFoundError(
            f"MultiHRI Overcooked source is missing: {overcooked_src}")
    sys.path.insert(0, str(overcooked_src))
    import overcooked_ai_py.mdp.overcooked_mdp as overcooked_mdp
    loaded_module = Path(overcooked_mdp.__file__).resolve()
    if not loaded_module.is_relative_to(overcooked_src):
        raise RuntimeError(
            f"loaded non-MultiHRI Overcooked module: {loaded_module}; "
            f"expected under {overcooked_src}")
    sys.path.insert(0, str(ROOT))
    from oai_agents.common.arguments import get_arguments
    from oai_agents.agents.agent_utils import load_agent
    from oai_agents.gym_environments.base_overcooked_env import OvercookedGymEnv
    from stable_baselines3.common.evaluation import evaluate_policy
    import random
    import numpy as np
    start = time.perf_counter()
    argv = sys.argv
    try:
        sys.argv = [argv[0]]
        args = get_arguments()
    finally:
        sys.argv = argv
    args.device = torch.device('cpu')
    args.num_players = task['players']
    args.teammates_len = task['players'] - 1
    args.layout_names = [task['layout']]
    args.horizon = task['max_steps']
    args.encoding_fn = 'OAI_egocentric'
    ego = load_agent(Path(task['ego_path']), args)
    teammates = [load_agent(Path(task['team_path']), args)
                 for _ in range(task['players'] - 1)]
    env = OvercookedGymEnv(args=args, layout_name=task['layout'],
                          is_eval_env=True, horizon=task['max_steps'],
                          deterministic=False, learner_type='originaler')
    env.set_teammates(teammates)
    env.set_reset_p_idx(0)
    if env.mdp.num_players != task['players']:
        raise ValueError('layout player count does not match requested team size')
    episode_seed = task['seed'] + task['episode']
    random.seed(episode_seed)
    np.random.seed(episode_seed)
    torch.manual_seed(episode_seed)
    print(f"START {task['method']} n={task['players']} layout={task['layout']} "
          f"ego_seed={task['ego_seed']} episode={task['episode']}", flush=True)
    steps = []
    total = 0.0
    from overcooked_ai_py.mdp.actions import Action
    def record_step(local, _global):
        nonlocal total
        reward = float(local['reward'])
        total += reward
        joint = env.prev_actions
        steps.append({'timestep': len(steps),
                      'executed_ego_action': int(np.asarray(local['actions']).reshape(-1)[0]),
                      'partner_actions': [Action.ACTION_TO_INDEX[a] for a in joint[1:]],
                      'reward': reward, 'total_reward': total})
    try:
        returns, lengths = evaluate_policy(ego, env, n_eval_episodes=1,
                                          deterministic=False, warn=False,
                                          return_episode_rewards=True,
                                          callback=record_step)
    finally:
        env.close()
    if len(steps) != lengths[0] or not math.isclose(total, returns[0], abs_tol=1e-5):
        raise AssertionError('trace and SB3 episode return disagree')
    result = {**semantic, "signature": signature, "ego_path": task["ego_path"],
              "team_path": task["team_path"], "episode_seed": task["seed"] + task["episode"],
              "return": returns[0], "steps": steps,
              "wall_time_s": time.perf_counter() - start,
              "job_id": os.environ.get("SLURM_JOB_ID"), "completed_at": time.time()}
    if task["method"] == "sp" and task["ego_seed"] == CANONICAL[task["players"]]:
        reference = json.loads(REFERENCE.read_text())
        if task["max_steps"] == reference["max_steps"] and task["seed"] == reference["seed"]:
            expected = reference["returns"][task["layout"]][task["episode"]]
            result["reference_return"] = expected
            result["reference_verified"] = bool(returns[0] == expected)
            result['reference_protocol'] = 'COMBO execution; native mHRI anti-stuck behavior may differ'
    atomic_json(path, result)
    print(f"DONE ego_seed={task['ego_seed']} episode={task['episode']} "
          f"return={returns[0]} seconds={result['wall_time_s']:.1f}", flush=True)
    return result


def statistics_row(rows):
    returns = [r["return"] for r in rows]
    means = [statistics.mean(r["return"] for r in rows if r["ego_seed"] == s)
             for s in sorted({r["ego_seed"] for r in rows})]
    return {"mean": statistics.mean(means), "episodes": len(rows),
            "checkpoints": len(means),
            "pooled_episode_sem": statistics.stdev(returns) / math.sqrt(len(returns))
            if len(returns) > 1 else None,
            "checkpoint_sem": statistics.stdev(means) / math.sqrt(len(means))
            if len(means) > 1 else None}


def export(output, rows, manifest):
    rows = sorted(rows, key=lambda r: (r["ego_seed"], r["episode"]))
    keys = ("method", "players", "layout", "ego_seed", "episode", "episode_seed",
            "return", "wall_time_s", "job_id", "ego_path", "team_path")
    for name, fields, data in (
            ("episodes.csv", keys, [{k: r[k] for k in keys} for r in rows]),
            ("steps.csv", (*keys[:6], "timestep", "executed_ego_action", "partner_actions",
                           "reward", "total_reward"),
             [{**{k: r[k] for k in keys[:6]}, **s,
               "partner_actions": json.dumps(s["partner_actions"])}
              for r in rows for s in r["steps"]])):
        temporary = output / f".{name}.tmp"
        with temporary.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(data)
        temporary.replace(output / name)
    summary = {**statistics_row(rows), "manifest": manifest,
               "per_checkpoint": {str(s): statistics_row([r for r in rows if r["ego_seed"] == s])
                                  for s in sorted({r["ego_seed"] for r in rows})}}
    atomic_json(output / "summary.json", summary)
    fields = ("scope", "ego_seed", "mean", "episodes", "checkpoints",
              "pooled_episode_sem", "checkpoint_sem")
    temporary = output / ".summary.csv.tmp"
    with temporary.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerow({"scope": "method", "ego_seed": "", **statistics_row(rows)})
        for seed, stats in summary["per_checkpoint"].items():
            writer.writerow({"scope": "checkpoint", "ego_seed": seed, **stats})
    temporary.replace(output / "summary.csv")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--players", type=int, choices=(3, 5), required=True)
    parser.add_argument("--layout", choices=("asymmetric_advantages", "coordination_ring",
                                           "counter_circuit", "cramped_room"), required=True)
    parser.add_argument("--method", choices=tuple(SEEDS), required=True)
    parser.add_argument("--multihri_root", type=Path, required=True)
    parser.add_argument("--multihri_overcooked_src", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--episodes", type=int, default=16)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--max_steps", type=int, default=400)
    parser.add_argument("--ego_seed", type=int)
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.episodes <= 16 or args.workers < 1 or not 1 <= args.max_steps <= 400:
        parser.error("episodes must be 1..16, workers >=1, max_steps 1..400")
    candidates = policies(args.multihri_root.resolve(), args.players, args.method)
    overcooked_src = args.multihri_overcooked_src or (
        args.multihri_root / "overcooked_ai" / "src")
    overcooked_src = overcooked_src.resolve()
    if not (overcooked_src / "overcooked_ai_py" / "mdp" / "overcooked_mdp.py").is_file():
        parser.error(f"MultiHRI Overcooked source not found: {overcooked_src}")
    if args.ego_seed is not None:
        candidates = [p for p in candidates if p["ego_seed"] == args.ego_seed]
        if not candidates:
            parser.error("ego_seed not in the method's verified pool")
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    source_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    manifest = {"method": args.method, "players": args.players,
                "layout": f"{args.players}_chefs_{args.layout}", "seed": args.seed,
                "episodes_per_checkpoint": args.episodes, "max_steps": args.max_steps,
                "checkpoint_policies": candidates, "revision": revision,
                "multihri_root": str(args.multihri_root.resolve()),
                "execution_revision": source_hash,
                "overcooked_implementation": str(overcooked_src),
                "multihri_revision": subprocess.check_output(
                    ["git", "rev-parse", "HEAD"], cwd=args.multihri_root.resolve(),
                    text=True).strip(),
                "reward": "shared sparse return (unduplicated sparse reward sum)",
                "protocol": "replace slot 0; fixed canonical SP teammates; native mHRI SB3 evaluation; stochastic; anti-stuck enabled",
                "held_out_teammate_training_exposure": "not verified"}
    print(json.dumps(manifest, indent=2), flush=True)
    if args.preflight:
        return
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    manifest_path = output / "manifest.json"
    if manifest_path.exists():
        previous = json.loads(manifest_path.read_text())
        if ({k: v for k, v in previous.items() if k != "revision"}
                != {k: v for k, v in manifest.items() if k != "revision"}):
            raise ValueError(f"incompatible manifest: {manifest_path}")
        manifest = previous
    atomic_json(manifest_path, manifest)
    completed = []
    with concurrent.futures.ProcessPoolExecutor(
            max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as executor:
        for policy in candidates:
            tasks = [{**manifest, **policy,
                      "multihri_overcooked_src": str(overcooked_src), "episode": ep,
                      "episode_path": str(output / "episodes" / f"seed{policy['ego_seed']}_ep{ep:02d}.json")}
                     for ep in range(args.episodes)]
            futures = [executor.submit(run_episode, task) for task in tasks]
            for future in concurrent.futures.as_completed(futures):
                completed.append(future.result())
                # Episode JSONs are the recovery source; exports refresh per checkpoint.
            export(output, completed, manifest)
            print(f"CHECKPOINT COMPLETE seed={policy['ego_seed']} "
                  f"episodes_saved={len(completed)}", flush=True)


if __name__ == "__main__":
    main()
