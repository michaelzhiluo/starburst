# ===================== Fig. 10 - Ablate Pareto ===================== #

# Ablating over waiting policies and their pareeto curves (assuming OO scheduling for all)
# 25% waiting budget - (constant-0.5, linear_cost-0.04, linear_runtime-0.25, linear_capacity-0.2)
python run_simulator_sweep.py \
--sched_alg fifo \
--dataset helios_gen \
--cluster_size 64 \
--cpus_per_node 48 \
--arrival_rate 36 \
--total_jobs 300000 \
--waiting_policy constant-0 constant-0.1 contant-0.25 constant-0.5 constant-1 constant-2 constant-4 constant-5 constant-7 constant-8 constant-16 constant-32  constant-64 constant-128 constant-256 \
constant-512 constant-1024 constant-2048 \
linear_cost-0 linear_cost-0.02 linear_cost-0.04 linear_cost-0.08 linear_cost-0.12 linear_cost-0.16 linear_cost-0.2 linear_cost-0.16 linear_cost-0.32 linear_cost-0.64 linear_cost-1.28 \
linear_cost-2.56 linear_cost-5.12 linear_cost-10.24 linear_cost-20.48  linear_cost-40.96 linear_cost-81.92 linear_cost-163.84 linear_cost-327.68 linear_cost-655.36  \
linear_runtime-0 linear_runtime-0 linear_runtime-0.1 linear_runtime-0.25 linear_runtime-0.5 linear_runtime-1 linear_runtime-2 linear_runtime-4 linear_runtime-8 \
linear_runtime-16 linear_runtime-32 linear_runtime-64 linear_runtime-128 linear_runtime-256 \
linear_capacity-0 linear_capacity-0.05 linear_capacity-0.1 linear_capacity-0.2  linear_capacity-0.3  linear_capacity-0.38 linear_capacity-0.5 linear_capacity-0.6 linear_capacity-0.8 linear_capacity-1 linear_capacity-2 linear_capacity-4 linear_capacity-8 linear_capacity-16 \
linear_capacity-32 linear_capacity-64 linear_capacity-128 linear_capacity-256 linear_capacity-512 \
--loop 1 \
--long_job_thres -1 0.25 \
--preempt_cloud_ratio -1 3 \
--seed 1337 \
--filter_name ablate_waiting_policy_pareto \
--log  ~/logs/ablate_waiting_policies_pareto.log


# Ablating over pareto curve for with and without OO scheduling.
python run_simulator_sweep.py \
--sched_alg fifo \
--dataset philly_gen \
--cluster_size 64 \
--arrival_rate 32 \
--total_jobs 300000 \
--waiting_policy linear_cost-0 linear_cost-0.04 linear_cost-0.06 linear_cost-0.08 linear_cost-0.1 linear_cost-0.12 linear_cost-0.16 linear_cost-0.32 linear_cost-0.64 linear_cost-1.28 \
linear_cost-2.56 linear_cost-5.12 linear_cost-10.24 linear_cost-20.48  linear_cost-40.96 linear_cost-81.92 linear_cost-163.84 linear_cost-327.68 linear_cost-655.36  \
linear_capacity-0 linear_capacity-0.2 linear_capacity-0.4 linear_capacity-0.6 linear_capacity-0.8  linear_capacity-1.2 linear_capacity-1.6 linear_capacity-3.2 \ linear_capacity-6.4 linear_capacity-12.8 linear_capacity-25.6 linear_capacity-51.2 linear_capacity-102.4 linear_capacity-204.8 linear_capacity-409.6 linear_capacity-819.2 linear_capacity-1638.4 linear_capacity-3276.8 linear_capacity-6553.6 \
--loop 0 1 \
--long_job_thres -1 0.25 \
--preempt_cloud_ratio -1 3 \
--seed 1337 \
--filter_name ablate_out_of_order_pareto \
--log  ~/logs/ablate_out_of_order_pareto.log