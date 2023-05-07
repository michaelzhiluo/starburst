
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

### Switch to Google Cloud Project and Region

Creating a Kubernetes cluster with 8 V100 GPUs on GCP and deploying Kubeflow involves several steps. Here's a detailed, end-to-end guide to help you through the process.

1. Set up the GCP environment:
   a. Sign up for a Google Cloud Platform (GCP) account, if you don't have one, and create a new project.
   b. Install the Google Cloud SDK (gcloud) on your local machine: https://cloud.google.com/sdk/docs/install
   c. Authenticate with your GCP account using the following command:
      ```
      gcloud auth login
      ```
   d. Set the default GCP project and region:
      ```
      gcloud config set project <your-project-id>
      gcloud config set compute/region <your-region>
      ```
   e. Enable the required APIs:
      ```
      gcloud services enable container.googleapis.com
      gcloud services enable compute.googleapis.com
      gcloud services enable iam.googleapis.com
      gcloud services enable iap.googleapis.com
      ```

2. Create a Kubernetes cluster with GPU nodes:
   a. Enable GPU support for your GCP project:
      ```
      gcloud compute project-info add-metadata --metadata enable-guest-attributes=TRUE
      ```
   b. Create a GPU node pool with 8 V100 GPUs:
      ```
      ./start_gke.sh
      ```
   c. If you see `CRITICAL: ACTION REQUIRED: gke-gcloud-auth-plugin, which is needed for continued use of kubectl, was not found or is not executable.`

      Follow the instruction here: https://cloud.google.com/blog/products/containers-kubernetes/kubectl-auth-changes-in-gke 

   d. Install the NVIDIA GPU device plugin for Kubernetes:
      ```
      kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/master/nvidia-driver-installer/cos/daemonset-preloaded.yaml
      ```

3. Install and set up kubectl:
   a. Install kubectl on your local machine: https://kubernetes.io/docs/tasks/tools/install-kubectl/
   b. Configure kubectl to use your GCP Kubernetes cluster:
      ```
      gcloud container clusters get-credentials skyburst-gpu --zone us-central1-c
      ```

4. Deploy Kubeflow to the cluster:
   a. Download and install the Kubeflow CLI (kfctl) from the GitHub releases page: https://github.com/kubeflow/kfctl/releases
   b. Set up the environment variables:
      ```
      export KF_NAME=<kubeflow-deployment-name>
      export BASE_DIR=<path-to-kubeflow-storage>
      export KF_DIR=${BASE_DIR}/${KF_NAME}
      ```
   c. Download the latest Kubeflow configuration file:
      ```
      export CONFIG_URI="https://raw.githubusercontent.com/kubeflow/manifests/master/kfdef/kfctl_gcp_iap.v1.3.0.yaml"
      ```
   d. Create and apply the Kubeflow configuration:
      ```
      mkdir -p ${KF_DIR}
      cd ${KF_DIR}
      kfctl apply -V -f ${CONFIG_URI}
      ```

5. Submit PyTorchJob using Kubeflow Operator:
   a. Create a YAML file (e.g., `pytorchjob.yaml`) containing the following PyTorchJob definition:

      ```yaml
      apiVersion: kubeflow.org/v1
      kind: PyTorchJob
      metadata:
        name: pytorch-job
      spec:
        pytorchReplicaSpecs:
          Master:
            replicas: 1
            restartPolicy: OnFailure
            template:


### Kuberflow pytorch jobs

https://www.kubeflow.org/docs/components/training/pytorch/

https://googlecloudplatform.github.io/kubeflow-gke-docs/docs/pipelines/enable-gpu-and-tpu/


```
# check the cluster
kubectl get nodes -o wide

# install kuberflow pytorch operator
# https://github.com/kubeflow/training-operator#installation
kubectl apply -k "github.com/kubeflow/training-operator/manifests/overlays/standalone?ref=v1.5.0"

# run the job
kubectl create -f simple.yaml

# to delete the job (if required)
kubectl delete pytorchjobs pytorch-simple -n kubeflow

# monitor the job
kubectl get -o yaml pytorchjobs pytorch-simple -n kubeflow
```

