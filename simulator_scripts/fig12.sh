# ===================== Fig. 12 - P90/99 Waiting Times ===================== #

# Ablating 90th, 99th percentile waiting time
python run_simulator_sweep.py \
--dataset helios \
--cluster_size 16 20 24 28 32 36 40 44 48 \
52 56 60 64 68 72 76 80 84 88 92 96 100 \
104 108 112 116 120 124 132 136 140 144 \
--cpus_per_node 48 \
--sched_alg fifo \
--waiting_policy constant-0.454 linear_cost_filter_cpu-0.04 linear_capacity_filter_cpu-0.2 \
--max_queue_length 10 1000000 \
--loop 0 1 \
--long_job_thres -1 0.25 \
--preempt_cloud_ratio -1 3 \
--seed 1994 \
--filter_name ablate_jct_percentile \
--log ~/logs/ablate_jct_percentile.log
