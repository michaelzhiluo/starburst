# Starburst ⭐: A Cost-aware Scheduler for Cloud Bursting

**Usenix ATC'24 Artifact Evaluation**

# Abstract

This guide is designed you to set up, run experiments, and replicate evaluation for Starburst. We split this document into 3 sections:

- **Setup**: How to setup Starburst (both simulator and our real-world experiments) in your Python environment OR through Docker.
- **Simulator Exps**: Run all our simulation experiments and replicate our results.
- **Real-World Exps**: Run our schedulers over Kubernetes on-prem cluster and run job submission pipeline. We place this last, as it is much more complicated and takes much longer to run.

# Setup


## Simulation Experiments

We note that all our runs logs are saved in the Google Cloud Storage, `gs://starburst-bucket/logs`. Our results can be directly fetched from this bucket and directly plotted with the Jupyter notebooks provided in `skyburst/plots`. However, we also provide bash commands to replicate the experiments below.

### Fig 7: End2End Simulator Results

### Fig 8: End2End Pareto Curves


## Real System Experiments

