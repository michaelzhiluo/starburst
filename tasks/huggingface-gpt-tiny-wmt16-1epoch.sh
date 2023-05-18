#!/bin/bash

# ETA:

# 1 GPU: 10h
# 2 GPU: 6h30m
# 4 GPU: 5h30m
# 8 GPU: 5h30m

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
python $SCRIPT_DIR/huggingface-gpt-wmt16.py \
    --per_device_train_batch_size 16 \
    --n_embd 256 \
    --n_layer 4 \
    --n_head 4 \
    --num_train_epochs 1
