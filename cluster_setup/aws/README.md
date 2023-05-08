
## Setup

```
conda create -n skyburst python=3.10
```

### Installing or updating kubectl

https://docs.aws.amazon.com/eks/latest/userguide/install-kubectl.html

```
# Kubernetes 1.26
curl -O https://s3.us-west-2.amazonaws.com/amazon-eks/1.26.2/2023-03-17/bin/darwin/amd64/kubectl
chmod +x ./kubectl
mkdir -p $HOME/bin && mv ./kubectl $HOME/bin/kubectl && export PATH=$HOME/bin:$PATH
echo 'export PATH=$PATH:$HOME/bin' >> ~/.bash_profile
```

test it

```
kubectl version --short --client
```

### Installing or updating eksctl

https://github.com/weaveworks/eksctl/blob/main/README.md#installation

```
# NOTE: this will also make brew installing kubectl, maybe conflict with the earlier step
brew tap weaveworks/tap
brew install weaveworks/tap/eksctl
```

### Kuberflow pytorch jobs

https://www.kubeflow.org/docs/components/training/pytorch/

https://googlecloudplatform.github.io/kubeflow-gke-docs/docs/pipelines/enable-gpu-and-tpu/


```
# create a cluster
eksctl create cluster --name skyburst --region us-east-1

# check the cluster
kubectl get nodes -o wide

# install kuberflow pytorch operator
# https://github.com/kubeflow/training-operator#installation
kubectl apply -k "github.com/kubeflow/training-operator/manifests/overlays/standalone?ref=v1.5.0"

# run the job
kubectl create -f simple.yaml

# monitor the job
kubectl get -o yaml pytorchjobs pytorch-simple -n kubeflow
```

