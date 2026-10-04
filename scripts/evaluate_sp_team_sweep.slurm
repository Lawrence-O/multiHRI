#!/bin/bash
#SBATCH --job-name=sp-team-sweep
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
case "${PLAYERS:?}" in
  3) CANONICAL=1010 ;;
  5) CANONICAL=13 ;;
  *) exit 2 ;;
esac
for TEAM_SEED in 13 68 1010 2020 2602; do
  [[ "$TEAM_SEED" == "$CANONICAL" ]] && continue
  "$PYTHON" -u scripts/evaluate_fixed_sp.py \
    --players "$PLAYERS" --layout "${LAYOUT:?}" --method "${METHOD:?}" \
    --team_seed "$TEAM_SEED" --multihri_root "$PWD" \
    --multihri_overcooked_src "$PWD/overcooked_ai/src" \
    --workers "${SLURM_CPUS_PER_TASK}" --episodes 16 --seed 0 --max_steps 400 \
    --output "results/nagent_sp_team_sweep_20261004/${PLAYERS}/${LAYOUT}/${METHOD}/team${TEAM_SEED}"
done
