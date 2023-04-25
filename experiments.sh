



# Run Philly trace (arrival and job char. depends on trace)
python run_simulator_sweep.py \
--dataset philly
--cluster_size 16 20 24 28 32 36 40 44 48 \
52 56 60 64 68 72 76 80 84 88 92 96 100 \
104 108 112 116 120 124 132 136 140 144 \
--sched_alg fifo \
--waiting_policy zero-1 linear_runtime-1.1 linear_runtime-1.25 \
linear_runtime-1.5 linear_runtime-2 \
--seed 5


# Run Philly trace with Poisson arrival (job char. depends on trace)
python run_simulator_sweep.py \
--sched_alg fifo \
--dataset gen_gpu \
--arrival 8 12 16 20 21 22 23 24 25 26 27 28 32 34 \
36 40 44 48 52 56 60 64 68 72 76 80 84 88 92 \
--total_jobs 300000 \
--waiting_policy zero-1 constant-1 linear_runtime-1.25 \
--predict_wait 1 \
--seed 5


# Run Philly trace with Poisson arrival varying CV (burstiness)
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

# Run M/M/c queueing theory simulator
python run_simulator_sweep.py \
--sched_alg fifo \
--dataset gen_gpu \
--arrival 40 44 48 52 56 60 64 68 72 76 \
80 84 88 92 96 100 104 108 112 116 \
--total_jobs 300000 \
--waiting_policy zero-1 constant-1 linear_runtime-1.25 \
--backfill 1 \
--predict_wait 1 \
--seed 5
