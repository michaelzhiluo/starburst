import argparse
import multiprocessing

num_cpu = multiprocessing.cpu_count()
from transformers import BertConfig, BertForSequenceClassification, BertTokenizerFast
from transformers import Trainer, TrainingArguments
from datasets import load_dataset

# Argument parser
parser = argparse.ArgumentParser()

parser.add_argument('--language_pair', type=str, default='fi-en')

parser.add_argument('--vocab_size', type=int, default=30522)
parser.add_argument('--hidden_size', type=int, default=256)
parser.add_argument('--num_hidden_layers', type=int, default=4)
parser.add_argument('--num_attention_heads', type=int, default=4)

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
  intermediate_size=args.hidden_size * 4
)

# Instantiate a new BERT model
model = BertForSequenceClassification(config)

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


dataset = load_dataset('wmt16', args.language_pair)

# Load the BERT tokenizer
tokenizer = BertTokenizerFast.from_pretrained('bert-base-multilingual-cased')


# Tokenize the dataset
def tokenize_function(examples):
    # We need to encode the source and target texts, and to provide both input IDs and attention mask
    # For translation tasks, the labels are the input IDs of the target text
    src_text = examples['translation']['fi']
    tgt_text = examples['translation']['en']
    inputs = tokenizer(src_text, truncation=True, padding="max_length", max_length=128)
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(tgt_text, truncation=True, padding="max_length", max_length=128)["input_ids"]
    inputs["labels"] = labels
    return inputs


tokenized_datasets = dataset.map(tokenize_function, batched=True, num_proc=num_cpu, remove_columns=["translation"])

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
    train_dataset=tokenized_datasets['train'],
    # eval_dataset=dataset['validation'],
)

# Train the model
trainer.train()

# Save the model
model.save_pretrained(args.output_dir)
