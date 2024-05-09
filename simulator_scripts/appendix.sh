# ===================== Appendix ===================== #

# Ablating Constant-Wait and Loop for Short vs Long waits.
python run_simulator_sweep.py \
--sched_alg fifo \
--dataset philly_gen \
--arrival 8 12 16 20 24 26 28 \
32 34 36 40 44 48 52 56 60 64 68 72 76 80 84 88 92 \
--total_jobs 450000 \
--sched_alg fifo \
--loop 0 1 \
--waiting_policy zero-0 constant-0.25 constant-4 \
--seed 1001 \
--filter_name appendix_constant_loop \
--log ~/logs/appendix/constant_loop_ablate.log


# Ablating Out-of-Order vs. Backfill (requires reservations).
python run_simulator_sweep.py \
--sched_alg fifo \
--dataset philly_gen \
--arrival 8 12 16 20 24 25 26 27 28 \
32 34 36 40 44 48 52 56 60 64 68 72 76 80 84 88 92 \
--cv_factor 0.5 1 2 4 8 16 \
--total_jobs 300000 \
--waiting_policy zero-1 linear_cost-0.076 \
--backfill 0 1 \
--loop 0 1 \
--predict_wait 0 \
--seed 1001 \
--filter_name backfill_appendix \
--log ~/logs/appendix/backfill.log \


# Data Gravity/ Data locality
python run_simulator_sweep.py \
--dataset philly \
--cluster_size 16 20 24 28 32 36 40 44 48 \
52 56 60 64 68 72 76 80 84 88 92 96 100 \
104 108 112 116 120 124 132 136 140 144 \
--sched_alg fifo \
--waiting_policy zero-1 constant-1 linear_cost-0.076 \
--max_queue_length 30 1000000 \
--data_gravity -1 0.25 \
--loop 0 1 \
--seed 1994 \
--filter_name philly_data_gravity \
--log ~/logs/appendix/philly_data_gravity.log

# Ablating job-offloading heuristics
python run_simulator_sweep.py \
--dataset helios \
--cpus_per_node 48 \
--cluster_size 16 20 24 28 32 36 40 44 48 \
52 56 60 64 68 72 76 80 84 88 92 96 100 \
104 108 112 116 120 124 132 136 140 144 \
--sched_alg fifo \
--waiting_policy zero-1 linear_cost-0.04 linear_cost_filter_cpu-0.04 \
--max_queue_length 10 1000000 \
--loop 1 \
--seed 1994 \
--filter_name ablate_job_offload \
--log ~/logs/appendix/jct_offload.log