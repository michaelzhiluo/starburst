import argparse
import multiprocessing

num_cpu = multiprocessing.cpu_count()
from transformers import BertConfig, BertForMaskedLM, BertTokenizerFast
from transformers import Trainer, TrainingArguments
from datasets import load_dataset

# Argument parser
parser = argparse.ArgumentParser()

parser.add_argument('--dataset', type=str, default='wmt16')

parser.add_argument('--vocab_size', type=int, default=30522)
parser.add_argument('--hidden_size', type=int, default=768)
parser.add_argument('--num_hidden_layers', type=int, default=12)
parser.add_argument('--num_attention_heads', type=int, default=12)
parser.add_argument('--intermediate_size', type=int, default=3072)

parser.add_argument('--output_dir', type=str, default='./results')
parser.add_argument('--num_train_epochs', type=int, default=3)
parser.add_argument('--per_device_train_batch_size', type=int, default=16)
parser.add_argument('--per_device_eval_batch_size', type=int, default=64)
parser.add_argument('--warmup_steps', type=int, default=500)
parser.add_argument('--weight_decay', type=float, default=0.01)
parser.add_argument('--gradient_accumulation_steps', type=int, default=1)

parser.add_argument('--logging_dir', type=str, default='./logs')
parser.add_argument('--logging_steps', type=int, default=10)

args = parser.parse_args()

# Define the configuration of GPT-2
config = BertConfig(
  vocab_size=args.vocab_size,
  hidden_size=args.hidden_size,
  num_hidden_layers=args.num_hidden_layers,
  num_attention_heads=args.num_attention_heads,
  intermediate_size=args.intermediate_size
)

# Instantiate a new BERT model
model = BertForMaskedLM(config)

# Datasets:
# ====================================================
# name                     train    validation    test
# ----------------------------------------------------
# wmt16 (de-en)          4548885          1014    1000
# wikitext-103-raw-v1    1801350          3760    4358
# wikitext-103-v1        1801350          3760    4358
# wikitext-2-raw-v1        36718          3760    4358
# wikitext-2-v1            36718          3760    4358
# ====================================================


if args.dataset == 'wmt16':
  # Load the WMT-16 dataset
  dataset = load_dataset('wmt16', 'de-en')
elif args.dataset == 'wikitext-103':
    # Load the WikiText-103 dataset
    dataset = load_dataset('wikitext', 'wikitext-103-raw-v1')
elif args.dataset == 'wikitext-2':
    # Load the WikiText-2 dataset
    dataset = load_dataset('wikitext', 'wikitext-2-raw-v1')


# Load the BERT tokenizer
tokenizer = BertTokenizerFast.from_pretrained('bert-base-uncased')


# Tokenize the dataset
def tokenize_function(examples):
    tokenized_input = tokenizer(examples["text"], truncation=True, padding="max_length", max_length=512)
    tokenized_input["labels"] = tokenized_input["input_ids"].copy()
    return tokenized_input


tokenized_datasets = dataset.map(tokenize_function, batched=True, num_proc=num_cpu, remove_columns=["text"])

# Define the training arguments
training_args = TrainingArguments(
    output_dir=args.output_dir,
    num_train_epochs=args.num_train_epochs,
    per_device_train_batch_size=args.per_device_train_batch_size,
    per_device_eval_batch_size=args.per_device_eval_batch_size,
    warmup_steps=args.warmup_steps,
    weight_decay=args.weight_decay,
    logging_dir=args.logging_dir,
    logging_steps=args.logging_steps,
    fp16=True,
    gradient_accumulation_steps=args.gradient_accumulation_steps,
    do_train=True,
    # do_eval=True,
)

# Define the trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset['train'],
    # eval_dataset=dataset['validation'],
)

# Train the model
trainer.train()

# Save the model
model.save_pretrained(args.output_dir)
