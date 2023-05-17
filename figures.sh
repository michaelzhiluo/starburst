# Section 3
# Background figure
python run_simulator_sweep.py \
--sched_alg fifo \
--dataset philly_gen \
--arrival 8 12 16 20 24 26 28 \
32 34 36 40 44 48 52 56 60 64 68 72 76 80 84 88 92 \
--cv_factor 8 \
--total_jobs 300000 \
--waiting_policy zero-1 infinite-1 \
linear_cost-0.076 \
--predict_wait 0 1 \
--loop 0 1 \
--seed 1001 \
--log /home/gcpuser/starburst_logs/background/results.log


# For Section 3.2
python run_simulator_sweep.py \
--sched_alg fifo \
--dataset philly_gen \
--arrival 8 12 16 20 24 26 28 \
32 34 36 40 44 48 52 56 60 64 68 72 76 80 84 88 92 \
--total_jobs 450000 \
--waiting_policy zero-1 constant-1 constant-2 constant-4 constant-8 \
--seed 1001 \
--log /home/gcpuser/starburst_logs/motivation/constant_ablate.log \


# For Section 3.2 Plotting areas of cluster underutilization. (Snapshot)
python run_simulator_sweep.py \
--sched_alg fifo \
--dataset philly_gen \
--arrival 28 30 32 52 \
--total_jobs 200000 \
--waiting_policy zero-1 constant-1 constant-2 constant-4 constant-8 \
--seed 1002 \
--log /home/gcpuser/starburst_logs/motivation/snapshot.log \
--snapshot 1

#==========================================
# Evaluation Section
#==========================================


# temp = []
# print(len(run_configs))
# for r in run_configs:
#     print(r['waiting_policy'])
#     if r['waiting_policy'] == 'zero-1':
#         if r['loop'] == 0 and r['backfill'] == 0:
#             temp.append(r)
#     elif r['waiting_policy'] == 'linear_cost-0.076':
#         if r['loop'] == 0 and r['backfill'] == 1:
#             temp.append(r)
#         elif r['loop'] == 1 and r['backfill'] == 0:
#             temp.append(r)
#         elif r['loop'] == 0 and r['backfill'] == 0:
#             temp.append(r)
# run_configs = temp
# For Showing loop versus backfill scheduling
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
--seed 999 \
--log /home/gcpuser/starburst_logs/motivation/loop.log \



# Evaluation: Helios Trace over different waiting policies
# python run_simulator_sweep.py \
# --dataset helios \
# --cpus_per_node 48 \
# --cluster_size 16 20 24 28 32 36 40 44 48 \
# 52 56 60 64 68 72 76 80 84 88 92 96 100 \
# 104 108 112 116 120 124 132 136 140 144 \
# --sched_alg fifo \
# --waiting_policy zero-1 constant-0.454 linear_cost-0.04 linear_runtime-1.25 \
# linear_capacity-0.234 \
# --seed 1994 \
# --log /home/gcpuser/starburst_logs/evaluation/waiting_policies.log

python run_simulator_sweep.py \
--dataset helios_gen \
--cpus_per_node 48 \
--cluster_size 64 \
--arrival 8 12 16 20 24 25 26 27 28 \
32 34 36 40 44 48 52 56 60 64 68 72 76 80 84 88 92 \
--total_jobs 300000 \
--sched_alg fifo \
--waiting_policy zero-1 constant-0.454 linear_cost-0.04 linear_runtime-1.25 \
linear_capacity-0.234 \
--loop 1 \
--seed 1994 \
--log /home/gcpuser/starburst_logs/evaluation/waiting_policies_gen.log


# Evaluation: Helios Trace: over waiting policies with and without loop
# python run_simulator_sweep.py \
# --dataset helios \
# --cpus_per_node 48 \
# --cluster_size 16 20 24 28 32 36 40 44 48 \
# 52 56 60 64 68 72 76 80 84 88 92 96 100 \
# 104 108 112 116 120 124 132 136 140 144 \
# --sched_alg fifo \
# --waiting_policy zero-1 constant-0.454 linear_cost_filter_cpu-0.04 \
# --loop 0 1 \
# --seed 1994 \
# --log /home/gcpuser/starburst_logs/evaluation/policies_loop.log \

python run_simulator_sweep.py \
--dataset helios_gen \
--cpus_per_node 48 \
--cluster_size 64 \
--arrival 8 12 16 20 24 25 26 27 28 \
32 34 36 40 44 48 52 56 60 64 68 72 76 80 84 88 92 \
--total_jobs 300000 \
--sched_alg fifo \
--waiting_policy zero-1 constant-0.454 linear_cost_filter_cpu-0.04 \
--loop 0 1 \
--seed 1994 \
--log /home/gcpuser/starburst_logs/evaluation/policies_loop_gen.log

# temp = []
# print(len(run_configs))
# for r in run_configs:
#     if r['waiting_policy'] == 'zero-1':
#         if r['max_queue_length'] == 1000000:
#             temp.append(r)
#     elif r['waiting_policy'] == 'linear_cost-0.04':
#         if r['max_queue_length'] == 1000000:
#             temp.append(r)
#     elif r['waiting_policy'] == 'linear_cost_filter_cpu-0.04':
#         temp.append(r)
# print(len(temp))
# run_configs = temp
# import pdb
# pdb.set_trace()
# Evaluation: Helios Trace over JCT reducing techniques
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
--log /home/gcpuser/starburst_logs/evaluation/jct.log \



# temp = []
# print(len(run_configs))
# for r in run_configs:
#     print(r['waiting_policy'])
#     if r['waiting_policy'] == 'zero-1':
#         if r['loop'] == 0 and r['max_queue_length'] == 1000000:
#             temp.append(r)
#     elif r['waiting_policy'] == 'constant-0.454':
#         if r['loop'] == 0 and r['max_queue_length'] == 1000000:
#             temp.append(r)
#     elif r['waiting_policy'] == 'linear_cost_filter_cpu-0.04':
#         if r['loop'] == 1 and r['max_queue_length'] == 10:
#             temp.append(r)
# print(len(temp))
# run_configs = temp
# import pdb
# pdb.set_trace()
# Evaluation: Helios Trace End2End
python run_simulator_sweep.py \
--dataset helios \
--cluster_size 16 20 24 28 32 36 40 44 48 \
52 56 60 64 68 72 76 80 84 88 92 96 100 \
104 108 112 116 120 124 132 136 140 144 \
--cpus_per_node 48 \
--sched_alg fifo \
--waiting_policy zero-1 constant-0.454 linear_cost_filter_cpu-0.04 \
--max_queue_length 10 1000000 \
--loop 0 1 \
--seed 1994 \
--log /home/gcpuser/starburst_logs/evaluation/helios.log






# temp = []
# print(len(run_configs))
# for r in run_configs:
#     print(r['waiting_policy'])
#     if r['waiting_policy'] == 'zero-1':
#         if r['loop'] == 0 and r['max_queue_length'] == 1000000:
#             temp.append(r)
#     elif r['waiting_policy'] == 'constant-1':
#         if r['loop'] == 0 and r['max_queue_length'] == 1000000:
#             temp.append(r)
#     elif r['waiting_policy'] == 'linear_cost-0.076':
#         if r['loop'] == 1 and r['max_queue_length'] == 30:
#             temp.append(r)
# print(len(temp))
# run_configs = temp
# import pdb
# pdb.set_trace()
# Evaluation: Philly Trace End2End
python run_simulator_sweep.py \
--dataset philly \
--cluster_size 16 20 24 28 32 36 40 44 48 \
52 56 60 64 68 72 76 80 84 88 92 96 100 \
104 108 112 116 120 124 132 136 140 144 \
--sched_alg fifo \
--waiting_policy zero-1 constant-1 linear_cost-0.076 \
--max_queue_length 30 1000000 \
--loop 0 1 \
--seed 1994 \
--log /home/gcpuser/starburst_logs/evaluation/philly.log



# temp = []
# print(len(run_configs))
# for r in run_configs:
#     if r['waiting_policy'] == 'zero-1':
#         if r['time_estimator_error'] == 0:
#             temp.append(r)
#     elif r['waiting_policy'] == 'linear_capacity_filter_cpu-0.234':
#         if r['time_estimator_error'] == 0:
#             temp.append(r)
#     elif r['waiting_policy'] == 'linear_cost_filter_cpu-0.04':
#         temp.append(r)
# print(len(temp))
# run_configs = temp
# import pdb
# pdb.set_trace()
# With time estimator errors
# python run_simulator_sweep.py \
# --dataset helios \
# --cpus_per_node 48 \
# --cluster_size 16 20 24 28 32 36 40 44 48 \
# 52 56 60 64 68 72 76 80 84 88 92 96 100 \
# 104 108 112 116 120 124 132 136 140 144 \
# --sched_alg fifo \
# --waiting_policy zero-1 linear_capacity_filter_cpu-0.234 linear_cost_filter_cpu-0.04 \
# --time_estimator_error 0 10 25 50 100 200 500 \
# --loop 1 \
# --seed 1994 \
# --max_queue_length 30 \
# --log /home/gcpuser/starburst_logs/evaluation/time_estimator_error.log

python run_simulator_sweep.py \
--dataset helios_gen \
--cpus_per_node 48 \
--cluster_size 64 \
--arrival 8 12 16 20 24 25 26 27 28 \
32 34 36 40 44 48 52 56 60 64 68 72 76 80 84 88 92 96 100 \
--total_jobs 300000 \
--sched_alg fifo \
--time_estimator_error 0 10 25 50 100 200 \
--waiting_policy zero-1 linear_cost_filter_cpu-0.04 \
--loop 1 \
--seed 1994 \
--max_queue_length 30 \
--log /home/gcpuser/starburst_logs/evaluation/time_estimator_error_gen.log




# Without and without timeestimator
# Evaluation: Helios Trace over different waiting policies
python run_simulator_sweep.py \
--dataset helios \
--cpus_per_node 48 \
--cluster_size 16 20 24 28 32 36 40 44 48 \
52 56 60 64 68 72 76 80 84 88 92 96 100 \
104 108 112 116 120 124 132 136 140 144 \
--sched_alg fifo \
--waiting_policy zero-1 linear_cost_filter_cpu-0.04 linear_capacity_filter_cpu-0.234 \
--loop 1 \
--seed 1994 \
--max_queue_length 30 \
--log /home/gcpuser/starburst_logs/evaluation/no_time_estimator.log




# With different levels of burstiness
python run_simulator_sweep.py \
--sched_alg fifo \
--dataset philly_gen \
--arrival 8 12 16 20 24 25 26 27 28 \
32 34 36 40 44 48 52 56 60 64 68 72 76 80 84 88 92 \
--cv_factor 1 4 8 16 \
--total_jobs 300000 \
--max_queue_length 30 \
--waiting_policy zero-1 linear_cost_filter_cpu-0.076 \
--seed 1000 \
--log  /home/gcpuser/starburst_logs/evaluation/burst.log



# Philly pareto curve
# With different levels of burstiness
python run_simulator_sweep.py \
--sched_alg fifo \
--dataset philly_gen \
--cluster_size 64 \
--arrival_rate 32 \
--total_jobs 600000 \
--waiting_policy constant-0 constant-0.5 constant-1 constant-2 constant-4 constant-5 constant-7 constant-8 constant-16 constant-32  constant-64 constant-128 constant-256 \
constant-512 constant-1024 constant-2048 \
linear_cost-0 linear_cost-0.04 linear_cost-0.08 linear_cost-0.12 linear_cost-0.16 linear_cost-0.32 linear_cost-0.64 linear_cost-1.28 \
linear_cost-2.56 linear_cost-5.12 linear_cost-10.24 linear_cost-20.48  linear_cost-40.96 linear_cost-81.92 linear_cost-163.84 linear_cost-327.68 linear_cost-655.36  \
--seed 1337 \
--log  /home/gcpuser/starburst_logs/evaluation/pareto.log





# Pareto Curve
# python run_simulator_sweep.py \
# --cluster_size 8 \
# --sched_alg sjf \
# --dataset synthetic \
# --arrival 2 4 6 8 10 12 14 16 \
# --total_jobs 20000 \
# --waiting_policy constant-0 constant-0.1 constant-0.25 constant-0.5 constant-1 constant-2 constant-4 constant-8 \
# linear_runtime-1 linear_runtime-1.1 linear_runtime-1.25 linear_runtime-1.5 linear_runtime-2 linear_runtime-3 linear_runtime-5 linear_runtime-9 \
# --seed 1001 \
# --log  /home/gcpuser/starburst_logs/synthetic/runs.log
