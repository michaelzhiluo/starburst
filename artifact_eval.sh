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
--log /home/gcpuser/final_logs/eval/helios_end2end.log


# =====================Figure 8 Pareto Curve End2End ===================== #

# Pareto curve: Philly Trace.
# 25% waiting budget - (constant-1, linear_cost-0.08, linear_capacity-0.8)
python run_simulator_sweep.py \
--sched_alg fifo \
--dataset philly_gen \
--cluster_size 64 \
--arrival_rate 32 \
--total_jobs 300000 \
--waiting_policy constant-0 constant-0.5 constant-1 constant-2 constant-4 constant-5 constant-7 constant-8 constant-16 constant-32  constant-64 constant-128 constant-256 \
constant-512 constant-1024 constant-2048 constant-4096 constant-8192 constant-16384 constant-32768 constant-65536 \
linear_cost-0 linear_cost-0.02 linear_cost-0.04 linear_cost-0.06 linear_cost-0.08 linear_cost-0.12 linear_cost-0.16 linear_cost-0.32 linear_cost-0.64 linear_cost-1.28 \
linear_cost-2.56 linear_cost-5.12 linear_cost-10.24 linear_cost-20.48 linear_cost-40.96 linear_cost-81.92 linear_cost-163.84 linear_cost-327.68 linear_cost-655.36  \
linear_capacity-0 linear_capacity-0.2 linear_capacity-0.4 linear_capacity-0.6 linear_capacity-0.8  linear_capacity-1.2 linear_capacity-1.6 linear_capacity-3.2 \ linear_capacity-6.4 linear_capacity-12.8 linear_capacity-25.6 linear_capacity-51.2 linear_capacity-102.4 linear_capacity-204.8 linear_capacity-409.6 linear_capacity-819.2 linear_capacity-1638.4 linear_capacity-3276.8 linear_capacity-6553.6 \
--long_job_thres -1 0.25 \
--preempt_cloud_ratio -1 3 \
--loop 0 1 \
--seed 1337 \
--filter_name philly_pareto \
--log  ~/logs/philly_pareto.log


# Pareto curve: Helios Trace.
# 25% waiting budget - (constant-0.5, linear_cost_filter_cpu-0.04, linear_capacity_filter_cpu-0.2)
python run_simulator_sweep.py \
--sched_alg fifo \
--dataset helios_gen \
--cluster_size 64 \
--arrival_rate 36 \
--total_jobs 300000 \
--waiting_policy constant-0 constant-0.5 constant-1 constant-2 constant-4 constant-5 constant-7 constant-8 constant-16 constant-32  constant-64 constant-128 constant-256 \
constant-512 constant-1024 constant-2048 constant-20 \
linear_cost_filter_cpu-0 linear_cost_filter_cpu-0.02 linear_cost_filter_cpu-0.04 linear_cost_filter_cpu-0.06 linear_cost_filter_cpu-0.08 linear_cost_filter_cpu-0.12 linear_cost_filter_cpu-0.16 linear_cost_filter_cpu-0.32 linear_cost_filter_cpu-0.64 linear_cost_filter_cpu-1.28 \
linear_cost_filter_cpu-2.56 linear_cost_filter_cpu-5.12 linear_cost_filter_cpu-10.24 linear_cost_filter_cpu-20.48 linear_cost_filter_cpu-40.96 linear_cost_filter_cpu-81.92 linear_cost_filter_cpu-163.84 linear_cost_filter_cpu-327.68 linear_cost_filter_cpu-655.36  \
linear_capacity_filter_cpu-0 linear_capacity_filter_cpu-0.0625 linear_capacity_filter_cpu-0.125 linear_capacity_filter_cpu-0.2 linear_capacity_filter_cpu-0.375 linear_capacity_filter_cpu-0.5 inear_capacity_filter_cpu-0.75 linear_capacity_filter_cpu-1 linear_capacity_filter_cpu-2 linear_capacity_filter_cpu-4 linear_capacity_filter_cpu-8 linear_capacity_filter_cpu-16 linear_capacity_filter_cpu-32 linear_capacity_filter_cpu-64 linear_capacity_filter_cpu-128 linear_capacity_filter_cpu-256 linear_capacity_filter_cpu-512 linear_capacity_filter_cpu-1024 linear_capacity_filter_cpu-2048 linear_capacity_filter_cpu-4096 \
--loop 0 1 \
--long_job_thres -1 0.25 \
--preempt_cloud_ratio -1 3 \
--seed 1337 \
--filter_name helios_pareto \
--log  ~/logs/helios_pareto.log

# ===================== Fig. 9 - Ablate Waiting Policies ===================== #

# Ablating over waiting policies (assuming OO scheduling for all)
python run_simulator_sweep.py \
--dataset helios_gen \
--cpus_per_node 48 \
--cluster_size 64 \
--arrival 8 12 16 20 24 25 26 27 28 \
32 34 36 40 44 48 52 56 60 64 68 72 76 80 84 88 92 \
--total_jobs 300000 \
--sched_alg fifo \
--waiting_policy zero-1 constant-0.454 linear_cost-0.04 linear_runtime-0.25 linear_capacity-0.234 \
--preempt_cloud_ratio -1 3 \
--long_job_thres -1 0.25 \
--loop 1 \
--seed 1994 \
--filter_name ablate_waiting_policy \
--log ~/logs/ablate_waiting_policies.log


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
--log  /home/gcpuser/final_logs/eval/ablate_out_of_order_pareto.log

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


# ===================== Fig. 13 - Waiting Budget Ablations ===================== #

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
--log  ~/logs/ablate_philly_waiting_budget.log


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
linear_capacity_filter_cpu-0 linear_capacity_filter_cpu-0.05 linear_capacity_filter_cpu-0.08 linear_capacity_filter_cpu-0.14 linear_capacity_filter_cpu-0.2 linear_capacity_filter_cpu-0.4 linear_capacity_filter_cpu-0.5 linear_capacity_filter_cpu-0.8 \
linear_capacity_filter_cpu-1.6 linear_capacity_filter_cpu-3.2 linear_capacity_filter_cpu-6.4 linear_capacity_filter_cpu-8 linear_capacity_filter_cpu-16 linear_capacity_filter_cpu-32 linear_capacity_filter_cpu-64 linear_capacity_filter_cpu-128 \
linear_capacity_filter_cpu-256 linear_capacity_filter_cpu-512 linear_capacity_filter_cpu-1024 linear_capacity_filter_cpu-2048 linear_capacity_filter_cpu-4096 \
--long_job_thres -1 0.25 \
--preempt_cloud_ratio -1 3 \
--loop 1 \
--seed 1337 \
--filter_name ablate_helios_waiting_budget \
--log ~/logs/ablate_helios_waiting_budget.log

# ===================== Fig. 14 - Starburst over Bursty Workloads ===================== #

python run_simulator_sweep.py \
--sched_alg fifo \
--dataset philly_gen \
--arrival 8 12 16 20 24 25 26 27 28 \
32 34 36 40 44 48 52 56 60 64 68 72 76 80 84 88 92 \
--cv_factor 0.5 1 2 4 8 16 \
--total_jobs 300000 \
--waiting_policy zero-1 constant-1 linear_runtime-1.25 \
--predict_wait 1 \
--seed 5
--log ~/logs/burst.log

# ===================== Fig. 15 - Pareto Curve for Queueing and Binpacking ===================== #

# Scheduling Algorithm Pareto Curve
python run_simulator_sweep.py \
--sched_alg fifo sjf edf \
--dataset philly_gen \
--cluster_size 64 \
--arrival_rate 32 \
--total_jobs 300000 \
--waiting_policy linear_cost-0 linear_cost-0.02 linear_cost-0.04 linear_cost-0.08 linear_cost-0.12 linear_cost-0.16 linear_cost-0.32 linear_cost-0.64 linear_cost-1.28 \
linear_cost-2.56 linear_cost-5.12 linear_cost-10.24 linear_cost-20.48  linear_cost-40.96 linear_cost-81.92 linear_cost-163.84 linear_cost-327.68 \
--loop 1 \
--seed 1337 \
--log ~/logs/sched_alg_pareto.log



# Bin-packing Algorithm Pareto Curve
python run_simulator_sweep.py \
--sched_alg fifo \
--binpack_alg first-fit best-fit \
--dataset philly_gen \
--cluster_size 64 \
--arrival_rate 32 \
--total_jobs 300000 \
--waiting_policy linear_cost-0 linear_cost-0.02 linear_cost-0.04 linear_cost-0.08 linear_cost-0.12 linear_cost-0.16 linear_cost-0.32 linear_cost-0.64 linear_cost-1.28 \
linear_cost-2.56 linear_cost-5.12 linear_cost-10.24 linear_cost-20.48  linear_cost-40.96 linear_cost-81.92 linear_cost-163.84 linear_cost-327.68 \
--loop 1 \
--seed 1337 \
--log ~/logs/binpack_pareto.log


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
--log /home/gcpuser/final_logs/appendix/constant_loop_ablate.log

# Time Estimator Errors for Compute-Wait.


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
--log /home/gcpuser/final_logs/appendix/backfill.log \


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
--log /home/gcpuser/final_logs/appendix/philly_data_gravity.log

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
--log /home/gcpuser/final_logs/appendix/jct_offload.log