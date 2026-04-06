#!/usr/bin/env python
"""Validate HDF5 dataset files: shapes, keys, episode counts, NaN/Inf, action ranges."""
import h5py, os, numpy as np
from overcooked_ai_py.mdp.overcooked_mdp import OvercookedGridworld

datasets = {
    'datasets/2on3_sp':         {'num_players': 2, 'eps_per_layout': 200},
    'datasets/2on5_sp':         {'num_players': 2, 'eps_per_layout': 200},
    'datasets/forced_coord_3p': {'num_players': 3, 'eps_per_layout': 200},
}

HORIZON = 400
N_CHANNELS = 27
REQUIRED_KEYS = ['obs', 'actions', 'sparse_rewards', 'shaped_rewards', 'dones', 'policy_id']
ENV_INFO_KEYS = ['ep_sparse_r', 'ep_shaped_r', 'ep_length',
                 'ep_sparse_r_by_agent', 'ep_shaped_r_by_agent']

errors = []
total_files = 0

for ds_dir, meta in datasets.items():
    NP = meta['num_players']
    EPL = meta['eps_per_layout']
    print(f'\n=== {ds_dir} (expect {NP}P, {EPL} eps/layout) ===')
    if not os.path.isdir(ds_dir):
        errors.append(f'{ds_dir}: directory missing')
        continue

    files = sorted(f for f in os.listdir(ds_dir) if f.endswith('.h5'))
    print(f'  Files: {len(files)}')

    for fname in files:
        total_files += 1
        fpath = os.path.join(ds_dir, fname)
        layout = fname.replace('.h5', '')

        # Load layout to get grid dimensions
        try:
            mdp = OvercookedGridworld.from_layout_name(layout)
            W, H = mdp.width, mdp.height
        except Exception as e:
            errors.append(f'{fpath}: cannot load layout {layout}: {e}')
            continue

        with h5py.File(fpath, 'r') as f:
            ok = True

            # --- Required keys ---
            for k in REQUIRED_KEYS:
                if k not in f:
                    errors.append(f'{fpath}: missing key "{k}"')
                    ok = False
            if 'env_info' not in f:
                errors.append(f'{fpath}: missing env_info group')
                ok = False
            else:
                for k in ENV_INFO_KEYS:
                    if k not in f['env_info']:
                        errors.append(f'{fpath}: missing env_info/{k}')
                        ok = False

            if 'obs' not in f:
                continue

            E = f['obs'].shape[0]

            # --- Episode count ---
            if E != EPL:
                errors.append(f'{fpath}: {E} episodes != expected {EPL}')
                ok = False

            # --- Shapes ---
            checks = [
                ('obs',            f['obs'].shape,            (E, HORIZON+1, NP, W, H, N_CHANNELS)),
                ('actions',        f['actions'].shape,        (E, HORIZON, NP, 1)),
                ('sparse_rewards', f['sparse_rewards'].shape, (E, HORIZON, NP, 1)),
                ('shaped_rewards', f['shaped_rewards'].shape, (E, HORIZON, NP, 1)),
                ('dones',          f['dones'].shape,          (E, HORIZON, NP)),
                ('policy_id',      f['policy_id'].shape,      (E, NP)),
            ]
            for name, actual, expected in checks:
                if name in f and actual != expected:
                    errors.append(f'{fpath}: {name} {actual} != expected {expected}')
                    ok = False

            # --- env_info shapes ---
            if 'env_info' in f:
                for k in ['ep_sparse_r', 'ep_shaped_r', 'ep_length']:
                    if k in f['env_info'] and f['env_info'][k].shape != (E,):
                        errors.append(f'{fpath}: env_info/{k} shape {f["env_info"][k].shape} != ({E},)')
                        ok = False
                for k in ['ep_sparse_r_by_agent', 'ep_shaped_r_by_agent']:
                    if k in f['env_info'] and f['env_info'][k].shape != (E, NP):
                        errors.append(f'{fpath}: env_info/{k} shape {f["env_info"][k].shape} != ({E},{NP})')
                        ok = False

            # --- NaN / Inf in obs (sample first + last episode) ---
            for idx in [0, E-1]:
                sample = f['obs'][idx]
                if np.any(np.isnan(sample)) or np.any(np.isinf(sample)):
                    errors.append(f'{fpath}: NaN/Inf in obs[{idx}]')
                    ok = False

            # --- Action range [0,5] ---
            acts = f['actions'][:]
            if acts.min() < 0 or acts.max() > 5:
                errors.append(f'{fpath}: action range [{acts.min()},{acts.max()}] outside [0,5]')
                ok = False

            # --- Dones boolean-like ---
            dones = f['dones'][:]
            if not np.all((dones == 0) | (dones == 1)):
                errors.append(f'{fpath}: dones has non-boolean values')
                ok = False

            # --- ep_length within horizon ---
            if 'env_info' in f and 'ep_length' in f['env_info']:
                lengths = f['env_info']['ep_length'][:]
                if np.any(lengths < 1) or np.any(lengths > HORIZON):
                    errors.append(f'{fpath}: ep_length range [{lengths.min()},{lengths.max()}] outside [1,{HORIZON}]')
                    ok = False

            status = 'OK' if ok else 'FAIL'
            print(f'  {layout:45s}  E={E:4d}  grid={W}x{H}  {status}')

print(f'\n=== Summary ===')
print(f'Files checked: {total_files}')
if errors:
    print(f'ERRORS ({len(errors)}):')
    for e in errors:
        print(f'  - {e}')
else:
    print('All files passed validation!')
