#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
python $SCRIPT_DIR/huggingface-bert-wikitext.py \
    --dataset wikitext-103 \
    --per_device_train_batch_size 8 \
    --hidden_size 512 \
    --num_hidden_layers 4 \
    --num_attention_heads 8 \
    --num_train_epochs 1
