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
	--log /home/gcpuser/final_logs/eval/ablate_jct_percentile.log



# Ablating Waiting Budget for Philly
# 25% waiting budget - (constant-1, linear_cost-0.08, linear_capacity-0.8)
python run_simulator_sweep.py \
	--sched_alg fifo \
	--dataset philly_gen \
	--cluster_size 64 \
	--arrival_rate 32 \
	--total_jobs 300000 \
	--waiting_policy constant-0 constant-0.4 constant-1 constant-2 constant-4 constant-8 constant-16 constant-32  constant-64 constant-128 constant-256 \
	constant-512 constant-1024 constant-2048 \
	linear_cost-0 linear_cost-0.02 linear_cost-0.04 linear_cost-0.06 linear_cost-0.08 linear_cost-0.12 linear_cost-0.16 linear_cost-0.32 linear_cost-0.64 linear_cost-1.28 \
	linear_cost-2.56 linear_cost-5.12 linear_cost-10.24 linear_cost-20.48 linear_cost-40.96 linear_cost-81.92 linear_cost-163.84 linear_cost-327.68 linear_cost-655.36  \
	linear_capacity-0 linear_capacity-0.2 linear_capacity-0.32 linear_capacity-0.45 linear_capacity-0.6 linear_capacity-0.8  linear_capacity-1.2 linear_capacity-1.6 linear_capacity-3.2 \
	linear_capacity-6.4 linear_capacity-12.8 linear_capacity-25.6 linear_capacity-51.2 linear_capacity-102.4 linear_capacity-204.8 linear_capacity-409.6 linear_capacity-819.2 linear_capacity-1638.4 linear_capacity-3276.8 linear_capacity-6553.6 \
	--loop 1 \
	--long_job_thres -1 0.25 \
	--preempt_cloud_ratio -1 3 \
	--seed 1337 \
	--filter_name ablate_philly_waiting_budget \
	--log  /home/gcpuser/final_logs/eval/ablate_philly_waiting_budget.log


# Ablating Waiting Budget for Helios
# 25% waiting budget - (constant-1, linear_cost-0.08, linear_capacity-0.2)
python run_simulator_sweep.py \
	--sched_alg fifo \
	--dataset helios_gen \
	--cluster_size 64 \
	--arrival_rate 36 \
	--total_jobs 300000 \
	--waiting_policy constant-0 constant-0.2 constant-0.4 constant-0.8 constant-1.6 constant-3.2 constant-6.4 constant-12.8 constant-25.6 constant-51.2 constant-102.4  constant-128 constant-256 \
	constant-512 constant-1024 constant-2048 \
	linear_cost_filter_cpu-0 linear_cost_filter_cpu-0.02 linear_cost_filter_cpu-0.04 linear_cost_filter_cpu-0.06 linear_cost_filter_cpu-0.08 linear_cost_filter_cpu-0.12 linear_cost_filter_cpu-0.16 linear_cost_filter_cpu-0.32 linear_cost_filter_cpu-0.64 linear_cost_filter_cpu-1.28 \
	linear_cost_filter_cpu-2.56 linear_cost_filter_cpu-5.12 linear_cost_filter_cpu-10.24 linear_cost_filter_cpu-20.48 linear_cost_filter_cpu-40.96 linear_cost_filter_cpu-81.92 linear_cost_filter_cpu-163.84 linear_cost_filter_cpu-327.68 linear_cost_filter_cpu-655.36  \
	linear_capacity_filter_cpu-0 linear_capacity_filter_cpu-0.05 linear_capacity_filter_cpu-0.08 linear_capacity_filter_cpu-0.14  linear_capacity_filter_cpu-0.2 linear_capacity_filter_cpu-0.4 linear_capacity_filter_cpu-0.5 inear_capacity_filter_cpu-0.8 linear_capacity_filter_cpu-1.6 linear_capacity_filter_cpu-3.2 linear_capacity_filter_cpu-6.4 linear_capacity_filter_cpu-8 linear_capacity_filter_cpu-16 linear_capacity_filter_cpu-32 linear_capacity_filter_cpu-64 linear_capacity_filter_cpu-128 linear_capacity_filter_cpu-256 linear_capacity_filter_cpu-512 linear_capacity_filter_cpu-1024 linear_capacity_filter_cpu-2048 linear_capacity_filter_cpu-4096 \
	--long_job_thres -1 0.25 \
	--preempt_cloud_ratio -1 3 \
	--loop 1 \
	--seed 1337 \
	--filter_name ablate_helios_waiting_budget \
	--log /home/gcpuser/rebuttal_logs/evaluation/helios_waiting_budget.log
