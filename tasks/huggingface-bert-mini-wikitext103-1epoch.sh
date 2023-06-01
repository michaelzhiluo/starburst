#!/bin/bash

# ETA:
# 1 GPU: 2.5h
# 2 GPU: 2h
# 4 GPU: 2h
# 8 GPU: 2h

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
python $SCRIPT_DIR/huggingface-bert-wikitext.py \
    --dataset wikitext-103 \
    --per_device_train_batch_size 16 \
    --hidden_size 256 \
    --num_hidden_layers 4 \
    --num_attention_heads 4 \
    --num_train_epochs 1
