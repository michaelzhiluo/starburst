#!/bin/bash
job_name=$1
kubectl get -o yaml jobs "$1"
echo "======================"
kubectl get pods --selector=job-name="$1"
echo "======================"
# kubectl logs $(kubectl get pods --selector=job-name="$1" -o jsonpath='{.items[*].metadata.name}')
kubectl logs $(kubectl get pods --selector=job-name="$1" -o jsonpath='{.items[-1].metadata.name}')
