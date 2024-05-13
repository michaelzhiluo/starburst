import argparse
import yaml
from kubernetes import client, config
from pathlib import Path
import os

def read_yaml(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return data

def write_yaml(file_path, data):
    with open(file_path, 'w') as file:
        yaml.safe_dump(data, file, default_flow_style=False)

def fetch_node_name(pod_name, namespace='default'):
    # Configure API client
    config.load_kube_config()  # or config.load_incluster_config() if running inside a cluster
    v1 = client.CoreV1Api()

    try:
        pod_info = v1.read_namespaced_pod(pod_name, namespace)
        return pod_info.spec.node_name
    except client.exceptions.ApiException as e:
        print(f"Error fetching pod info: {e}")
        return None

def update_pod_nodes(log_path):
    file_path = Path(f'{log_path}/events/0.yaml')
    file_path = os.path.abspath(file_path)
    if not os.path.exists(file_path):
        raise ValueError(f'Incorrect path {file_path}')

    data = read_yaml(file_path)
    cluster = data["onprem"]
    if 'pod_node' in cluster:
        for pod in cluster['pod_node']:
            if cluster['pod_node'][pod] is None:
                node_name = fetch_node_name(pod)
                if node_name:
                    cluster['pod_node'][pod] = node_name
                    print(f"Updated {pod}: Node set to {node_name}")
                else:
                    print(f"Node name not found for {pod}")

    write_yaml(file_path, data)

def main():
    parser = argparse.ArgumentParser(description="Update Kubernetes pod nodes in YAML file.")
    parser.add_argument("--log_path", type=str, help="Path to the YAML file")
    args = parser.parse_args()

    update_pod_nodes(args.log_path)

if __name__ == "__main__":
    main()