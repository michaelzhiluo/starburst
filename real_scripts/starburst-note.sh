#!/bin/bash

# Get the directory where the script is located
script_dir="$(cd "$(dirname "../${BASH_SOURCE[0]}")" && pwd)"

# Change to that directory
cd "$script_dir"

# (Re)Deploy Chakra, the scheduler plugin.
kubectl delete deployment chakra-scheduler

kubectl apply -f chakra/chakra_admin.yaml

kubectl apply -f chakra/chakra.yaml

cd starburst/sweep

python submit_sweep.py --config ../sweep_examples/artifact_eval/starburst-note.yaml