"""
BatchedTeammateVecEnv: A VecEnv wrapper that batches teammate inference across
all environments for massive speedup. Instead of N_envs * N_teammates individual
forward passes per step, groups observations by policy and does one forward pass
per unique policy.
"""
from copy import deepcopy
from collections import defaultdict

import numpy as np
import torch as th
from stable_baselines3.common.vec_env import DummyVecEnv


class BatchedTeammateVecEnv(DummyVecEnv):
    """
    Drop-in replacement for DummyVecEnv that batches teammate neural network
    inference across all environments.

    On each step:
    1. Gather teammate observations from all envs
    2. Group by unique policy (id(policy)) and batch the forward passes
    3. Set pre-computed actions on each env
    4. Call env.step() which uses the pre-computed actions instead of individual predict()
    """

    def step_wait(self):
        # Phase 1: Gather teammate info from all envs
        all_env_teammate_info = []
        has_nn_teammates = False
        for env_idx in range(self.num_envs):
            env = self.envs[env_idx]
            if len(env.teammates) > 0:
                info = env.get_teammate_info_for_batching()
                all_env_teammate_info.append(info)
                if any(not is_custom for _, _, is_custom, _, _ in info):
                    has_nn_teammates = True
            else:
                all_env_teammate_info.append(None)

        # Phase 2: If there are NN teammates, batch their inference
        if has_nn_teammates:
            # Group observations by policy identity
            # Key: id(teammate_object) -> {policy, obs_list, indices}
            policy_groups = defaultdict(lambda: {'teammate': None, 'obs_keys': None, 'obs_list': [], 'indices': []})

            for env_idx in range(self.num_envs):
                env_info = all_env_teammate_info[env_idx]
                if env_info is None:
                    continue
                for tm_slot, (tm_obs, tm_id, is_custom, info, teammate) in enumerate(env_info):
                    if is_custom:
                        # CustomAgent: compute inline (no GPU), cheap
                        action = teammate.predict(obs=tm_obs, deterministic=self.envs[env_idx].deterministic, info=info)[0]
                        if all_env_teammate_info[env_idx][tm_slot] is not None:
                            # Store the action directly - will be assembled later
                            all_env_teammate_info[env_idx][tm_slot] = ('custom_done', action)
                    else:
                        group = policy_groups[tm_id]
                        group['teammate'] = teammate
                        # Filter obs keys to match policy's observation space
                        filtered_obs = {k: v for k, v in tm_obs.items() if k in teammate.policy.observation_space.keys()}
                        group['obs_list'].append(filtered_obs)
                        group['indices'].append((env_idx, tm_slot))

            # Batch forward pass per unique policy
            with th.no_grad():
                for tm_id, group in policy_groups.items():
                    teammate = group['teammate']
                    obs_list = group['obs_list']
                    if len(obs_list) == 0:
                        continue

                    # Stack observations into batched tensors
                    batched_obs = {}
                    for key in obs_list[0].keys():
                        stacked = np.stack([o[key] for o in obs_list], axis=0)
                        batched_obs[key] = stacked

                    # Single batched forward pass
                    actions = _batched_predict(teammate, batched_obs)

                    # Distribute actions back
                    for i, (env_idx, tm_slot) in enumerate(group['indices']):
                        all_env_teammate_info[env_idx][tm_slot] = ('nn_done', actions[i])

            # Phase 3: Set pre-computed actions on each env
            for env_idx in range(self.num_envs):
                env_info = all_env_teammate_info[env_idx]
                if env_info is None:
                    continue
                precomputed = []
                for item in env_info:
                    if isinstance(item, tuple) and len(item) == 2 and item[0] in ('custom_done', 'nn_done'):
                        precomputed.append(item[1])
                    else:
                        # Shouldn't happen, but fallback
                        precomputed.append(None)
                self.envs[env_idx].set_precomputed_teammate_actions(precomputed)

        # Phase 4: Normal DummyVecEnv stepping (env.step will use precomputed actions)
        for env_idx in range(self.num_envs):
            obs, self.buf_rews[env_idx], self.buf_dones[env_idx], self.buf_infos[env_idx] = self.envs[env_idx].step(
                self.actions[env_idx]
            )
            if self.buf_dones[env_idx]:
                self.buf_infos[env_idx]["terminal_observation"] = obs
                obs = self.envs[env_idx].reset()
            self._save_obs(env_idx, obs)
        return (self._obs_from_buf(), np.copy(self.buf_rews), np.copy(self.buf_dones), deepcopy(self.buf_infos))


def _batched_predict(teammate, batched_obs):
    """
    Run a batched forward pass through a teammate's policy.
    Input: batched_obs dict with arrays of shape (batch, ...)
    Output: numpy array of actions, shape (batch,)
    """
    policy = teammate.policy
    policy.set_training_mode(False)

    # Convert to tensors on the correct device
    obs_tensor = {}
    for key, val in batched_obs.items():
        obs_tensor[key] = th.as_tensor(val, device=policy.device).float()

    if hasattr(policy, "get_distribution"):
        if 'subtask_mask' in obs_tensor and np.prod(obs_tensor['subtask_mask'].shape[1:]) == policy.action_space.n:
            dist = policy.get_distribution(obs_tensor, action_masks=obs_tensor['subtask_mask'])
        else:
            dist = policy.get_distribution(obs_tensor)
        actions = dist.get_actions(deterministic=teammate.deterministic if hasattr(teammate, 'deterministic') else False)
    elif hasattr(policy, "q_net"):
        q_values = policy.q_net(obs_tensor)
        actions = th.argmax(q_values, dim=1)
    else:
        raise NotImplementedError("Policy does not support distribution extraction.")

    return actions.cpu().numpy().reshape(-1)
