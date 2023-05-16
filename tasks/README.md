# Tasks

Here is a summary of the configurations for the GPT-2 and BERT model variants:

**GPT-2:**

[paper](https://d4mucfpksywv.cloudfront.net/better-language-models/language_models_are_unsupervised_multitask_learners.pdf)
[repo](https://huggingface.co/gpt2)

- `small` (also called `117M` or `124M`): 12 layers (transformer blocks), 768 hidden size (dimension of the embedding vectors), 12 attention heads, and 117 million parameters.
- `medium` (also called `345M` or `355M`): 24 layers, 1024 hidden size, 16 attention heads.
- `large` (also called `774M`): 36 layers, 1280 hidden size, 20 attention heads.
- `extra large` (also called `1.5B`): 48 layers, 1600 hidden size, 25 attention heads.

**BERT:**

[repo](https://huggingface.co/prajjwal1/bert-mini)

- `tiny`: 2 layers (transformer blocks), 128 hidden size (dimension of the embedding vectors), 4 attention heads.
- `mini`: 4 layers (transformer blocks), 256 hidden size (dimension of the embedding vectors), 4 attention heads.
- `small`: 4 layers (transformer blocks), 512 hidden size (dimension of the embedding vectors), 8 attention heads.
- `medium`: 8 layers (transformer blocks), 512 hidden size (dimension of the embedding vectors), 8 attention heads.
- `base`: 12 layers (transformer blocks), 768 hidden size (dimension of the embedding vectors), 12 attention heads, 110 million parameters.
- `large`: 24 layers (transformer blocks), 1024 hidden size (dimension of the embedding vectors), 16 attention heads, 340 million parameters.

Please note that these are the typical configurations, but they can be adjusted based on specific needs or resource constraints.

## huggingface-gpt_wikitext-2

```bash
python huggingface-gpt.py --dataset wikitext-2 --per_device_train_batch_size 4 --num_train_epochs 3
```

1 GPU: 66m40.167s
2 GPU: 40m18.809s
4 GPU: 32m44.447s
8 GPU: 29m18.776s

## huggingface-gpt2_wikitext-103

```bash
time python huggingface-gpt.py --dataset wikitext-103 --per_device_train_batch_size 4 --gradient_accumulation_steps 2 --num_train_epochs 1
```

1 GPU: 40+h
2 GPU: 12-13h
4 GPU: 9-10h
8 GPU: 7-8h
