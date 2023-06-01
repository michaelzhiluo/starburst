FROM gcr.io/deeplearning-platform-release/pytorch-gpu.1-12
COPY tasks /tasks
RUN pip install scikit-learn==1.0.2 transformers==4.29.1 datasets==2.12.0 torchvision==0.13.1 accelerate==0.19.0
