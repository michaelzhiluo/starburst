# Starburst ⭐: A Cost-aware Scheduler for Cloud Bursting

**Usenix ATC'24 Artifact Evaluation**

# Abstract

This guide is designed you to set up, run experiments, and replicate evaluation for Starburst. We split this document into 3 sections:

- **Setup**: How to setup Starburst (both simulator and our real-world experiments) in your Python environment OR through Docker.
- **Simulator Exps**: Run all our simulation experiments and replicate our results.
- **Real-World Exps**: Run our schedulers over Kubernetes on-prem cluster and run job submission pipeline. We place this last, as it is much more complicated and takes much longer to run.

# Setup


## Simulation Experiments

We note that all our simulators logs for all our experiments (including Appendix) are saved in a public Google Cloud Storage bucket: `gs://starburst_bucket/logs`. If the user wants to save time, all our results can be directly fetched from this bucket and directly plotted with the Jupyter notebooks provided in `skyburst/plots`. 

To do so, install Gcloud and run the following command:
```
gsutil -m cp -r gs://starburst_bucket/logs ~/
```


However, we also provide bash commands below to generate the logs for each figure below. This is also provided in the repo, in `artifact_eval.sh`. Note that these simulator experiment can take  5min-1 hour to complete each for a 48 CPU machine.

### Fig 7: End2End Simulator Results

To run End2End experiments with both Philly and Helios traces, run:
```
# Philly End2End Experiments
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

# Helios End2End Experiments
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
--log ~/logs/helios_end2end.log
```

Use `skyburst/notebooks/fig7_simulator_end2end.ipynb` to plot with the outputted logs.

## Fig 8: End2End Pareto Curves



### Fig 9: 


## Real System Experiments

