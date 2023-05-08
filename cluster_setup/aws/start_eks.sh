#!/bin/bash
eksctl create cluster \
  --name skyburst \
  --nodegroup-name skyburst-nodegroup \
  --node-type p3.16xlarge \
  --nodes 1 \
  --region us-east-1
