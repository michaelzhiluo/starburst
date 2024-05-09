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
