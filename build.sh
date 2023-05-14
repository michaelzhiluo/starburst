#/bin/bash

# Build the docker image and push to GCR
docker build -t skyburst:latest .
docker tag skyburst:latest gcr.io/sky-burst/skyburst:latest
docker push gcr.io/sky-burst/skyburst:latest
