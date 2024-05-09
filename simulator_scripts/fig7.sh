# =====================Figure 7 End2End Simulation Results ===================== #

# Evaluation: Philly Trace End2End.
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
--filter_name philly_end2end \
--log ~/logs/philly_end2end.log

# Evaluation: Helios Trace End2End.
python run_simulator_sweep.py \
--dataset helios \
--cluster_size 16 20 24 28 32 36 40 44 48 \
52 56 60 64 68 72 76 80 84 88 92 96 100 \
104 108 112 116 120 124 132 136 140 144 \
--cpus_per_node 48 \
--sched_alg fifo \
--waiting_policy zero-1 constant-0.454 linear_cost_filter_cpu-0.04  linear_capacity_filter_cpu-0.234 \
--max_queue_length 10 1000000 \
--long_job_thres -1 0.25 \
--loop 0 1 \
--preempt_cloud_ratio -1 3 \
--seed 1994 \
--filter_name helios_end2end \
--log ~/logs/eval/helios_end2end.log