# ===================== Fig. 14 - Starburst over Bursty Workloads ===================== #

python run_simulator_sweep.py \
--sched_alg fifo \
--dataset philly_gen \
--arrival 8 12 16 20 24 25 26 27 28 \
32 34 36 40 44 48 52 56 60 64 68 72 76 80 84 88 92 \
--cv_factor 1 2 4 8 \
--total_jobs 300000 \
--loop 1 \
--max_queue_length 30 \
--waiting_policy zero-1 linear_cost_filter_cpu-0.076 \
--seed 1000 \
--log  ~/logs/burst.log