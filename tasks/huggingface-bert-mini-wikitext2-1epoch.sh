#!/bin/bash

# ETA:
# 1 GPU: 3-4m
# 2 GPU: 2-3m
# 4 GPU: 3-4m
# 8 GPU: 3-4m

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
python $SCRIPT_DIR/huggingface-bert-wikitext.py \
    --dataset wikitext-2 \
    --per_device_train_batch_size 16 \
    --hidden_size 256 \
    --num_hidden_layers 4 \
    --num_attention_heads 4 \
    --num_train_epochs 1
