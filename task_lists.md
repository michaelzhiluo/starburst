# SkyBurst Task Lists

For adjustable number of epochs, the job will run `--num_train_epochs` epochs. The default is 1 epoch for all models.
The total execution time is roughly the running time multiplied by the number of epochs.

For adjustable number of GPUs, the job will use all available GPUs on the node. The batch size we are using is proportional to the number of GPUs.
For example, if the batch size is 32 for 1 GPU, then the batch size will be 64 for 2 GPUs, 128 for 4 GPUs, and 256 for 8 GPUs.
With more GPUs, the tasks might be faster if the communication overhead is not too high.

NOTE: GPT-2 model is way bigger than BERT model. So we downside some GPT-2 models to make them comparable to BERT models (to make sure the running time is not too long).

The following table is the list of GPU jobs.
If we consider choices of #GPUs (1,2,4,8), then the total amount of jobs is ~80. This can be easily extented by changing the number of epochs, or submitting the same job with a different name.

The running time is a rough estimation with maximum number of GPUs (usually 8) and 1 epoch. For most of the jobs, running time with 1 GPU does not differ too much from 8 GPUs, except large models like BERT small, GPT-2 mini, GPT-2 small, where 8 GPUs would be 2-3x faster than 1 GPU.

| Index | Command Line                                                    | Model                           |    Dataset |   n_epochs |     n_gpus | Type | Running Time |
|-------|-----------------------------------------------------------------|---------------------------------|------------|------------|------------|------|--------------|
|     1 | /tasks/pytorch-regression.py                                    | N/A                             |        N/A |          1 |          1 | test |         ~1m  |
|     2 | /tasks/pytorch-mnist.py                                         | LeNet modern variant            |      MNIST | adjustable |          1 | test |         ~5m  |
|     3 | /tasks/pytorch-cifar10-efficientnet_v2_m.py                     | EfficientNet V2                 |    CIFAR10 | adjustable | adjustable |   CV |       5-10m  |
|     4 | /tasks/pytorch-cifar10-mobilenet_v3_small.py                    | MobileNet v3                    |    CIFAR10 | adjustable | adjustable |   CV |       5-10m  |
|     5 | /tasks/pytorch-cifar10-resnet50.py                              | ResNet-50                       |    CIFAR10 | adjustable | adjustable |   CV |       5-10m  |
|     6 | /tasks/tasks/pytorch-cifar10-resnet101.py                       | ResNet-101                      |    CIFAR10 | adjustable | adjustable |   CV |       5-10m  |
|     7 | /tasks/tasks/pytorch-cifar10-resnext50_32x4d.py                 | ResNext-50 (32x4d)              |    CIFAR10 | adjustable | adjustable |   CV |       5-10m  |
|     8 | /tasks/tasks/pytorch-cifar10-vgg11.py                           | VGG-11                          |    CIFAR10 | adjustable | adjustable |   CV |       5-10m  |
|     9 | /tasks/huggingface-bert-wikitext.py --dataset wikitext-2 --per_device_train_batch_size 32 --hidden_size 128 --num_hidden_layers 2  --num_attention_heads 4 | BERT (tiny)                           |  WikiText-2 | adjustable | adjustable |  NLP |       3-5m  |
|    10 | /tasks/huggingface-bert-wikitext.py --dataset wikitext-2 --per_device_train_batch_size 16 --hidden_size 256 --num_hidden_layers 4  --num_attention_heads 4 | BERT (mini)                           |  WikiText-2 | adjustable | adjustable |  NLP |      5-10m  |
|    11 | /tasks/huggingface-bert-wikitext.py --dataset wikitext-2 --per_device_train_batch_size 8 --hidden_size 512 --num_hidden_layers 4  --num_attention_heads 8 | BERT (small)                          |  WikiText-2 | adjustable | adjustable |  NLP |      5-10m  |
|    12 | /tasks/huggingface-bert-wikitext.py --dataset wikitext-103 --per_device_train_batch_size 32 --hidden_size 128 --num_hidden_layers 2  --num_attention_heads 4 | BERT (tiny)                           |  WikiText-103 | adjustable | adjustable |  NLP |     1h  |
|    13 | /tasks/huggingface-bert-wikitext.py --dataset wikitext-103 --per_device_train_batch_size 16 --hidden_size 256 --num_hidden_layers 4  --num_attention_heads 4 | BERT (mini)                           |  WikiText-103 | adjustable | adjustable |  NLP |     2h  |
|    14 | /tasks/huggingface-bert-wikitext.py --dataset wikitext-103 --per_device_train_batch_size 8 --hidden_size 512 --num_hidden_layers 4  --num_attention_heads 8 | BERT (small)                          |  WikiText-103 | adjustable | adjustable |  NLP |      4h  |
|    15 | /tasks/huggingface-gpt-wikitext.py --dataset wikitext-2 --per_device_train_batch_size 16 --n_embd 256 --n_layer 4 --n_head 4  | GPT-2 (tiny variant similar to BERT mini)  |  WikiText-2 | adjustable | adjustable |  NLP |       5m  |
|    16 | /tasks/huggingface-gpt-wikitext.py --dataset wikitext-2 --per_device_train_batch_size 8 --n_embd 512 --n_layer 8 --n_head 8 | GPT-2 (mini variant similar to BERT medium)  |  WikiText-2 | adjustable | adjustable |  NLP |       10m  |
|    17 | /tasks/huggingface-gpt-wikitext.py --dataset wikitext-2 --per_device_train_batch_size 4 --n_embd 768 --n_layer 12 --n_head 12 | GPT-2 (small)                          |  WikiText-2 | adjustable | adjustable |  NLP |      15m  |
|    18 | /tasks/huggingface-gpt-wikitext.py --dataset wikitext-103 --per_device_train_batch_size 16 --n_embd 256 --n_layer 4 --n_head 4  | GPT-2 (tiny variant similar to BERT mini)  |  WikiText-103 | adjustable | adjustable |  NLP |       2h  |
|    19 | /tasks/huggingface-gpt-wikitext.py --dataset wikitext-103 --per_device_train_batch_size 8 --n_embd 512 --n_layer 8 --n_head 8 | GPT-2 (mini variant similar to BERT medium)  |  WikiText-103 | adjustable | adjustable |  NLP |       4h  |
|    20 | /tasks/huggingface-gpt-wikitext.py --dataset wikitext-103 --per_device_train_batch_size 4 --n_embd 768 --n_layer 12 --n_head 12 | GPT-2 (small)                          |  WikiText-103 | adjustable | adjustable |  NLP |      7h  |
|    21 | /tasks/huggingface-gpt-wmt16.py --language_pair fi-en --per_device_train_batch_size 16 --n_embd 256 --n_layer 4 --n_head 4  | GPT-2 (tiny variant similar to BERT mini)  |  WMT-16 (fi-en pair) | adjustable | adjustable |  NLP |       2h  |
|    22 | /tasks/huggingface-gpt-wmt16.py --language_pair fi-en --per_device_train_batch_size 8 --n_embd 512 --n_layer 8 --n_head 8 | GPT-2 (mini variant similar to BERT medium)  |  WMT-16 (fi-en pair) | adjustable | adjustable |  NLP |       3h  |
|    23 | /tasks/huggingface-gpt-wmt16.py --language_pair fi-en --per_device_train_batch_size 4 --n_embd 768 --n_layer 12 --n_head 12 | GPT-2 (small)                          |  WMT-16 (fi-en pair) | adjustable | adjustable |  NLP |      6h  |
