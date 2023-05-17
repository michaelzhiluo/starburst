



# Run Philly trace (arrival and job char. depends on trace)
# Vary deadline values
python run_simulator_sweep.py \
--dataset philly \
--cluster_size 16 20 24 28 32 36 40 44 48 \
52 56 60 64 68 72 76 80 84 88 92 96 100 \
104 108 112 116 120 124 132 136 140 144 \
--sched_alg fifo \
--waiting_policy zero-1 linear_runtime-1.1 linear_runtime-1.25 \
linear_runtime-1.5 linear_runtime-2 \
--seed 5


# Run Philly trace (arrival and job char. depends on trace)
# Starburst = linear_cost + loop
python run_simulator_sweep.py \
--dataset philly \
--cluster_size 16 20 24 28 32 36 40 44 48 \
52 56 60 64 68 72 76 80 84 88 92 96 100 \
104 108 112 116 120 124 132 136 140 144 \
--sched_alg fifo \
--waiting_policy zero-1 constant-1 linear_runtime-1.25 \
linear_cost-0.076 \
--loop 0 1 \
--predict_wait 1 \
--seed 1337


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


# Run Philly trace with Poisson arrival varying prediction algorithm for waiting
python run_simulator_sweep.py \
--sched_alg fifo \
--dataset philly_gen \
--arrival 8 12 16 20 24 25 26 27 28 \
32 34 36 40 44 48 52 56 60 64 68 72 76 80 84 88 92 \
--cv_factor 4 \
--total_jobs 200000 \
--waiting_policy zero-1 linear_cost-0.076 \
--loop 1 \
--predict_wait 0 1 2 \
--seed 1901


python run_simulator_sweep.py \
--dataset philly \
--cluster_size 16 20 24 28 32 36 40 44 48 \
52 56 60 64 68 72 76 80 84 88 92 96 100 \
104 108 112 116 120 124 132 136 140 144 \
--sched_alg fifo \
--waiting_policy zero-1 linear_cost-0.076 \
--predict_wait 0 1 2 \
--loop 1 \
--seed 1903


# Run Philly trace with Poisson arrival varying CV (burstiness)
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
--log /home/gcpuser/starburst_logs/background/results

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


# Run Helios Venus trace (arrival and job char. depends on trace)
# Vary Waiting policy
python run_simulator_sweep.py \
--dataset helios \
--cluster_size 16 20 24 28 32 36 40 44 48 \
52 56 60 64 68 72 76 80 84 88 92 96 100 \
104 108 112 116 120 124 132 136 140 144 \
--sched_alg fifo \
--waiting_policy zero-1 linear_runtime-1.25 linear_cost-0.04 \
linear_runtime_filter_cpu-1.25 constant-0.454 \
--seed 2024


# Run Helios Venus trace (arrival and job char. depends on trace)
# Vary Scheudling algorithm (not much difference)
python run_simulator_sweep.py \
--dataset helios \
--cluster_size 16 20 24 28 32 36 40 44 48 \
52 56 60 64 68 72 76 80 84 88 92 96 100 \
104 108 112 116 120 124 132 136 140 144 \
--sched_alg fifo lifo swf sjf ljf \
--waiting_policy zero-1 linear_runtime-1.25 linear_cost-0.04 \
--predict_wait 1 \
--seed 5



# Check if loop works
python run_simulator_sweep.py \
--dataset helios \
--cluster_size 16 20 24 28 32 36 40 44 48 \
52 56 60 64 68 72 76 80 84 88 92 96 100 \
104 108 112 116 120 124 132 136 140 144 \
--sched_alg fifo \
--waiting_policy zero-1 linear_runtime-1.25 linear_cost-0.04 \
--predict_wait 1 \
--loop 0 1 \
--seed 5



# Loop over clipping time
python run_simulator_sweep.py \
--dataset helios \
--cluster_size 16 20 24 28 32 36 40 44 48 \
52 56 60 64 68 72 76 80 84 88 92 96 100 \
104 108 112 116 120 124 132 136 140 144 \
--sched_alg fifo \
--clip_time 48 24 12 6 \
--waiting_policy zero-1 linear_cost_filter_cpu-0.04 \
--predict_wait 1 \
--loop 0 1 \
--seed 1002


# Loop over filter cpu
python run_simulator_sweep.py \
--cpus_per_node 48 \
--dataset helios \
--cluster_size 16 20 24 28 32 36 40 44 48 \
52 56 60 64 68 72 76 80 84 88 92 96 100 \
104 108 112 116 120 124 132 136 140 144 \
--sched_alg fifo \
--clip_time 48 \
--waiting_policy zero-1 linear_runtime-1.25 linear_runtime_filter_cpu-1.25 linear_cost-0.04 linear_cost_filter_cpu-0.04 \
--predict_wait 1 \
--loop 0 1 \
--seed 1003



# 30 max queue length
python run_simulator_sweep.py \
--dataset philly \
--cluster_size 16 20 24 28 32 36 40 44 48 \
52 56 60 64 68 72 76 80 84 88 92 96 100 \
104 108 112 116 120 124 132 136 140 144 \
--sched_alg fifo \
--waiting_policy zero-1 linear_cost_filter_cpu-0.076 \
--predict_wait 0 1 \
--loop 1 \
--max_queue_length 5 10 15 20 25 30 35 100000000 \
--seed 1904




# 10
python run_simulator_sweep.py \
--dataset helios \
--cluster_size 16 20 24 28 32 36 40 44 48 \
52 56 60 64 68 72 76 80 84 88 92 96 100 \
104 108 112 116 120 124 132 136 140 144 \
--sched_alg fifo \
--waiting_policy zero-1 linear_cost_filter_cpu-0.04 \
--predict_wait 0 1 \
--loop 1 \
--max_queue_length 5 10 15 20 25 30 35 100000000 \
--seed 1904
