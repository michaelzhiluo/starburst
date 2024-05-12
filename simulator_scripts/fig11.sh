# ===================== Fig. 11 - Ablate Out-of-Order Scheduling ===================== #

# Ablating over OO scheduling.
python run_simulator_sweep.py \
--dataset philly \
--cluster_size 16 20 24 28 32 36 40 44 48 \
52 56 60 64 68 72 76 80 84 88 92 96 100 \
104 108 112 116 120 124 132 136 140 144 \
--sched_alg fifo \
--waiting_policy zero-1 constant-1 linear_cost-0.076 linear_capacity-0.77 \
--max_queue_length 30 1000000 \
--long_job_thres -1 0.25 \
--loop 0 1 \
--preempt_cloud_ratio -1 3 \
--seed 1994 \
--filter_name philly_end2end_ablate_out_of_order \
--log ~/logs/philly_ablate_out_of_order.log