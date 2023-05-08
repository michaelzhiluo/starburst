import aiohttp
import asyncio
from datetime import datetime

import click
from fastapi import FastAPI, BackgroundTasks
from kubernetes import client, config, watch
from pydantic import BaseModel


# Configure Kubernetes client
config.load_kube_config()
kube_client = client.BatchV1Api()

app = FastAPI()
NAMESPACE = "default"
API_DOMAIN = "kubeflow.org"
API_VERSION = "v1"
API_PLURAL = "pytorchjobs"

class JobSchema(BaseModel):
    apiVersion: str
    kind: str
    metadata: dict
    spec: dict


async def submit_job_async(job_spec):
    # Submit the Kubernetes job using the provided job specification
    config.load_kube_config()
    api_base = config.kube_config.Configuration().host
    url = f"{api_base}/apis/{API_DOMAIN}/{API_VERSION}/namespaces/{NAMESPACE}/{API_PLURAL}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.kube_config.Configuration().api_key['authorization']}"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=job_spec, headers=headers) as response:
            if response.status == 201:
                print(f"Job {job_spec['metadata']['name']} submitted")
            else:
                print(f"Error: {response.status}")


async def cancel_job_async(job_name):
    # Cancel the specified PyTorchJob in the Kubernetes cluster
    config.load_kube_config()
    api_base = config.kube_config.Configuration().host
    url = f"{api_base}/apis/{API_DOMAIN}/{API_VERSION}/namespaces/{NAMESPACE}/{API_PLURAL}/{job_name}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.kube_config.Configuration().api_key['authorization']}"
    }

    async with aiohttp.ClientSession() as session:
        async with session.delete(url, headers=headers) as response:
            if response.status == 200:
                print(f"Job {job_name} canceled")
            else:
                print(f"Error: {response.status}")


async def job_completion_handler(job_name, job_duration):
    # Perform actions upon job completion, e.g., log the job duration
    print(f"Job {job_name} completed in {job_duration} seconds")


async def watch_jobs():
    # Monitor the status of submitted jobs and trigger appropriate event handlers
    w = watch.Watch()
    for event in w.stream(kube_client.list_namespaced_custom_object, group=API_DOMAIN, version=API_VERSION, namespace=NAMESPACE, plural=API_PLURAL):
        pytorch_job = event["object"]
        job_name = pytorch_job["metadata"]["name"]
        job_status = pytorch_job["status"]

        # Update the job completion condition according to the PyTorchJob status
        if job_status.get("conditions") and any(condition["type"] == "Succeeded" for condition in job_status["conditions"]):
            job_duration = job_status["completionTime"] - job_status["startTime"]
            await job_completion_handler(job_name, job_duration.total_seconds())
        # Add other conditions and monitoring logic as needed


@app.post("/submit_job")
async def submit_job_endpoint(job_schema: JobSchema, background_tasks: BackgroundTasks):
    # Use the job_schema to create the job spec
    job_spec = job_schema.dict()

    # Use background tasks to submit the job asynchronously
    background_tasks.add_task(submit_job_async, job_spec)
    return {"status": "Job submission in progress"}


@app.post("/cancel_job/{job_name}")
async def cancel_job_endpoint(job_name: str, background_tasks: BackgroundTasks):
    # Use background tasks to cancel the job asynchronously
    background_tasks.add_task(cancel_job_async, job_name)
    return {"status": "Job cancellation in progress"}


@app.on_event("startup")
async def startup_event():
    # Run watch_jobs as a background task when the application starts
    asyncio.create_task(watch_jobs())


@click.command()
@click.option("--host", default="0.0.0.0", help="Host to bind the server to.")
@click.option("--port", default=8000, help="Port to bind the server to.")
def main(host: str, port: int):
    import uvicorn

    uvicorn.run("skyburst.scheduler.server:app", host=host, port=port, log_level="info", reload=True)


if __name__ == "__main__":
    main()
