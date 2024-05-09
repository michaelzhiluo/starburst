# ===================== Fig. 11 - Ablate Out-of-Order Scheduling ===================== #

# Ablating over OO scheduling.
python run_simulator_sweep.py \
--dataset helios_gen \
--cpus_per_node 48 \
--cluster_size 64 \
--arrival 8 12 16 20 24 25 26 27 28 \
32 34 36 40 44 48 52 56 60 64 68 72 76 80 84 88 92 \
96 100 104 108 112 116 \
--total_jobs 300000 \
--sched_alg fifo \
--waiting_policy zero-1 constant-0.454 linear_cost_filter_cpu-0.04 linear_capacity_filter_cpu-0.2 \
--loop 0 1 \
--long_job_thres -1 0.25 \
--preempt_cloud_ratio -1 3 \
--seed 1994 \
--filter_name ablate_out_of_order \
--log ~/logs/ablate_out_of_order.log