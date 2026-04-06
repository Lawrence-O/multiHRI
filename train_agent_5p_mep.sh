#!/bin/bash

ALGO="MEP"
TEAMMATES_LEN=4
HOW_LONG=5
NUM_OF_CKPOINTS=40
# Trimmed: 4 common layouts, actual 5-player
LAYOUT_NAMES="5_chefs_asymmetric_advantages,5_chefs_coordination_ring,5_chefs_counter_circuit,5_chefs_cramped_room"
EXP_DIR="Complex/5_trimmed_MEP"
TOTAL_EGO_AGENTS=4
QUICK_TEST=false

POP_FORCE_TRAINING=true
ADVERSARY_FORCE_TRAINING=false
PRIMARY_FORCE_TRAINING=false

source scripts/bash_scripts/env_config.sh
WANDB_MODE="disabled"

python scripts/train_agents.py \
    --layout-names ${LAYOUT_NAMES} \
    --algo-name ${ALGO} \
    --exp-dir ${EXP_DIR} \
    --num-of-ckpoints ${NUM_OF_CKPOINTS} \
    --teammates-len ${TEAMMATES_LEN} \
    --num-players ${NUM_PLAYERS} \
    --custom-agent-ck-rate-generation ${CUSTOM_AGENT_CK_RATE_GENERATION} \
    --num-steps-in-traj-for-dyn-adv ${NUM_STEPS_IN_TRAJ_FOR_DYN_ADV} \
    --num-static-advs-per-heatmap ${NUM_STATIC_ADVS_PER_HEATMAP} \
    --num-dynamic-advs-per-heatmap ${NUM_DYNAMIC_ADVS_PER_HEATMAP} \
    --use-val-func-for-heatmap-gen ${USE_VAL_FUNC_FOR_HEATMAP_GEN} \
    --prioritized-sampling ${PRIORITIZED_SAMPLING} \
    --n-envs ${N_ENVS} \
    --epoch-timesteps ${EPOCH_TIMESTEPS} \
    --pop-total-training-timesteps ${POP_TOTAL_TRAINING_TIMESTEPS} \
    --n-x-sp-total-training-timesteps ${N_X_SP_TOTAL_TRAINING_TIMESTEPS} \
    --fcp-total-training-timesteps ${FCP_TOTAL_TRAINING_TIMESTEPS} \
    --adversary-total-training-timesteps ${ADVERSARY_TOTAL_TRAINING_TIMESTEPS} \
    --n-x-fcp-total-training-timesteps ${N_X_FCP_TOTAL_TRAINING_TIMESTEPS} \
    --total-ego-agents ${TOTAL_EGO_AGENTS} \
    --wandb-mode ${WANDB_MODE} \
    --pop-force-training ${POP_FORCE_TRAINING} \
    --adversary-force-training ${ADVERSARY_FORCE_TRAINING} \
    --primary-force-training ${PRIMARY_FORCE_TRAINING} \
    --how-long ${HOW_LONG} \
    --exp-name-prefix "${EXP_NAME_PREFIX}"
