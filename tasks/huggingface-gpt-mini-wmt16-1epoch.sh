#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
python $SCRIPT_DIR/huggingface-gpt-wmt16.py \
    --per_device_train_batch_size 8 \
    --n_embd 512 \
    --n_layer 8 \
    --n_head 8 \
    --num_train_epochs 1
