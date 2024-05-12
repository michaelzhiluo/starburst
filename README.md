# Starburst ⭐: A Cost-aware Scheduler for Cloud Bursting

**Usenix ATC'24 Artifact Evaluation**

# Abstract

This guide is designed you to set up, run experiments, and replicate evaluation for Starburst. We split this document into 3 sections:

- **Setup**: How to setup Starburst (both simulator and our real-world experiments) in your Python environment OR through Docker.
- **Simulator Exps**: Run all our simulation experiments and replicate our results.
- **Real-World Exps**: Run our schedulers over Kubernetes on-prem cluster and run job submission pipeline. We place this last, as it is much more complicated and takes much longer to run.

# Setup

We provide several options for the evaluator to install Starburst.

## 1. Python Setup

Our codebase requires Python >= 3.9. To install dependencies for Starburst, run:
```
pip install -r requirements.txt
```

Install `git-lfs` by following the instructions listed [here](https://docs.github.com/en/repositories/working-with-files/managing-large-files/installing-git-large-file-storage)

Install the Philly and Helios traces with the follwoing code below:
```
cd ~/
git lfs clone https://github.com/msr-fiddle/philly-traces.git
cd philly-traces
tar -xvf trace-data.tar.gz 

cd ~/
git lfs clone https://github.com/S-Lab-System-Group/HeliosData
cd HeliosData
unzip data.zip
```

One of our experiments uses Gurobi to solve a mixed integeger linear program (MILP). As Gurobi is more difficult to setup (and the user may opt to SSH to our machine instead), we defer setup for Gurobi in the Simulator Experiment (Table 4) section.

## 2. SSH to VM

We also provide our private key for evaluators to run experiments in our VM, which already has everything setup! The VM contains the repositories for both simulator, real-world system, Gurobi, and the Philly/Helios traces.

For best expereince, we recommend linking VSCode remote explorer with the SSH'ed VM by modifying the SSH config file `~/.ssh/config`:

```
Host starburst
  HostName 34.121.144.68
  User gcpuser
  IdentityFile [PATH_TO_PRIVATE_KEY]
  IdentitiesOnly yes
  ForwardAgent yes
  StrictHostKeyChecking no
  UserKnownHostsFile=/dev/null
  GlobalKnownHostsFile=/dev/null
  Port 22
```

# Simulation Experiments

We note that all our simulators logs for all our experiments (including Appendix) are saved in a public Google Cloud Storage bucket: `gs://starburst_bucket/logs`. If the user wants to save time, all our results can be directly fetched from this bucket and directly plotted with the Jupyter notebooks provided in `skyburst/notebooks`. 

To do so, install Gcloud on your machine and run the following command to pull the logs from the bucket:
```
# Will download the logs to ~/log
gsutil -m cp -r gs://starburst_bucket/logs ~/
```

However, we also provide bash commands below to generate the logs for each figure below. This is also provided in the repo, in `skyburst/simulator_scripts`. Note that these experiments can take  5min-1 hour to complete on a 48 CPU machine.

## Fig 7: End2End Simulator Results

To run End2End experiments with both Philly and Helios traces, run:
```
simulator_scripts/fig7.sh
```

This will output logs to the path `~/logs/philly_end2end.log` and `~/logs/helios_end2end.log`.
Use `skyburst/notebooks/fig7_simulator_end2end.ipynb` to plot the graphs with the corresponding logs.

## Fig 8: End2End Pareto Curves

To run End2End pareto curve experiments with both Philly and Helios traces, run:
```
simulator_scripts/fig8.sh
```

This will output logs to the path `~/logs/philly_pareto.log` and `~/logs/helios_pareto.log`.
Use `skyburst/notebooks/fig8_pareto_ipynb.ipynb` to plot the graphs with the corresponding logs.


## Fig 9: Ablation over Waiting Policies.

To run ablations over different waiting policies, run:
```
simulator_scripts/fig9.sh
```

This will output logs to the path `~/logs/ablate_waiting_policies.log`.
Use `skyburst/notebooks/fig9_ablate_waiting_policy.ipynb` to plot the graphs with the corresponding logs.


## Fig 10: Ablation over Pareto Curves

To run ablations over the pareto curves for different waiting policies and out-of-order scheduling, run:
```
simulator_scripts/fig10.sh
```

This will output logs to the path `~/logs/ablate_waiting_policies_pareto.log` and `~/logs/ablate_out_of_order_pareto.log`.
Use `skyburst/notebooks/fig10_ablate_pareto.ipynb` to plot the graphs with the corresponding logs.

## Fig 11: Ablation over Out-of-Order Scheduling

To run ablations over out-of-order scheduling, run:
```
simulator_scripts/fig11.sh
```

This will output logs to the path `~/logs/ablate_out_of_order.log`.
Use `skyburst/notebooks/fig11_ablate_out_of_order.ipynb` to plot the graphs with the corresponding logs.


## Fig 12: P90/P99 Waiting Times

To run experiments over the 90th and 99th percentile waiting times, run:
```
simulator_scripts/fig12.sh
```

This will output logs to the path `~/logs/ablate_jct_percentile.log`.
Use `skyburst/notebooks/fig12_ablate_jct_percentile.ipynb` to plot the graphs with the corresponding logs.


## Fig 13: Ablate Waiting Budget

To run ablations over our waiting budget framework, run:
```
simulator_scripts/fig13.sh
```

This will output logs to the path `~/logs/ablate_philly_waiting_budget.log` and `~/logs/ablate_helios_waiting_budget.log`.
Use `skyburst/notebooks/fig13_ablate_waiting_budget.ipynb` to plot the graphs with the corresponding logs.

## Table 4: MILP Experiments

Our MILP experiments requires access to GUROBI, a popular mathematical optimization solver. However, Gurobi requires a license. We provide our license to the artifact evaluators in `gurobi.lic`.

### Setup Gurobi

The Gurboi Optimizer should already be installed from setting up the Python dependencies. To provide the license, place your `gurobi.lic` file in `/opt/gurobi` or your home directory. 

See `skyburst/notebooks/tab4_optimal_solver.ipynb` to run the MILP and evaluate it against Starburst and other baselines. Our experiments run the MILP for 8 hours; we recommend the reviewer to try either 4 or 8 hours. 

To run a headless version of the notebook, use the following command:
```
jupyter nbconvert --to notebook --execute 'skyburst/notebooks/tab4_optimal_solver.ipynb'--ExecutePreprocessor.timeout=-1
```

We also plot Gantt charts to show which jobs run on cluster and on cloud. An example is provided below, with captions to correctly interpret the Gantt chart:

<img src="gantt.svg" width=80% height=80%>


## Fig 14: Starburst w.r.t Bursty Workloads

To run ablations over bursty workloads (Starburst w.r.t different Coefficient of Variances for a Gamma arrival distribution), run:
```
simulator_scripts/fig14.sh
```

This will output logs to the path `~/logs/burst.log`.
Use `skyburst/notebooks/fig14_ablate_robustness.ipynb` to plot the graphs with the corresponding logs.

## Fig 15: Queueing and Binpacking Policies

To run pareto curves for Starburst over different queueing and binpacking policies, run:
```
simulator_scripts/fig15.sh
```

This will output logs to the path `~/logs/sched_alg_pareto.log` and `~/logs/binpack_pareto.log`.
Use `skyburst/notebooks/fig15_ablate_queue_binpack.ipynb` to plot the graphs with the corresponding logs.


# Real System Experiments

We note that our experiments evaluate over a 4 node, 8 V100/node cluster, which was provisoined as a GKE cluster on Google Cloud, with Skypilot for cloud jobs. This incurred $40K cloud costs during the development of Starburst, which vastly exceeded our allocated lab budget. Due to budgetary reasons, we show that Starburst can reduce 80% cloud costs:
 for a 4 node, 96-CPU cluster, while jobs that are sent to the cloud are **logged to a file** instead.

