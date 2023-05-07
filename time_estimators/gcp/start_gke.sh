#!/bin/bash
CLUSTER_NAME=skyburst-gpu
ZONE=us-central1-c
POOL_NAME=gpu-pool

gcloud container clusters create $CLUSTER_NAME \
    --num-nodes 1 \
    --accelerator "type=nvidia-tesla-v100,count=8" \
    --machine-type n1-standard-96 \
    --zone $ZONE \
    --cluster-version "latest" \
    --enable-autoupgrade \
    --enable-autorepair \
    --scopes cloud-platform \
    --network skypilot-vpc \
    --subnetwork skypilot-vpc

# create a note pool (a subset of nodes) out of the cluster for scheduling
gcloud container node-pools create $POOL_NAME \
  --cluster $CLUSTER_NAME \
  --machine-type n1-standard-96 \
  --accelerator "type=nvidia-tesla-v100,count=8" \
  --num-nodes 1 \
  --zone $ZONE

# delete the cluster
# gcloud container clusters delete $CLUSTER_NAME --zone $ZONE

