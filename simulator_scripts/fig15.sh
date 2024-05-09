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