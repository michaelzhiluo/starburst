#!/bin/bash

# ETA:
# 1 GPU: 20m
# 2 GPU: 15m
# 4 GPU: 10m
# 8 GPU: 10m
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
python $SCRIPT_DIR/huggingface-gpt-wikitext.py \
    --dataset wikitext-2 \
    --per_device_train_batch_size 16 \
    --n_embd 256 \
    --n_layer 4 \
    --n_head 4 \
    --num_train_epochs 1
