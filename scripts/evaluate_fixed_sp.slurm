#!/bin/bash
#SBATCH --job-name=native-fixed-sp
#SBATCH --account=ckpt-socialrl
#SBATCH --partition=ckpt-all
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=08:00:00
#SBATCH --requeue
#SBATCH --output=slurm_logs/%x-%j.out
#SBATCH --error=slurm_logs/%x-%j.err
set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$PWD/overcooked_ai/src:$PWD"
export MPLCONFIGDIR="/tmp/mpl-${USER}-${SLURM_JOB_ID}"
export XDG_CACHE_HOME="/tmp/xdg-${USER}-${SLURM_JOB_ID}"
mkdir -p "$MPLCONFIGDIR" "$XDG_CACHE_HOME"
PYTHON=/mmfs1/gscratch/socialrl/lawony/conda_envs/mHRI/bin/python
exec "$PYTHON" -u scripts/evaluate_fixed_sp.py \
  --players "${PLAYERS:?}" --layout "${LAYOUT:?}" --method "${METHOD:?}" \
  --multihri_root "$PWD" --multihri_overcooked_src "$PWD/overcooked_ai/src" \
  --workers "${SLURM_CPUS_PER_TASK}" --episodes "${EPISODES:-16}" \
  --seed 0 --max_steps 400 \
  --output "${OUTPUT_ROOT:-results/nagent_fixed_sp_native_20261003}/${PLAYERS}/${LAYOUT}/${METHOD}"
