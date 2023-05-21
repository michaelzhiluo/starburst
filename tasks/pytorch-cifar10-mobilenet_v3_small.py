import argparse
import multiprocessing

import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torchvision.models import mobilenet_v3_small

from tqdm import tqdm

cpu_count = multiprocessing.cpu_count()
device_count = torch.cuda.device_count()

assert device_count > 0, "No CUDA devices found"

# Transformations for the train and test sets
transform_train = transforms.Compose([
    transforms.RandomCrop(32, padding=4),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
])

transform_test = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
])

# Load the CIFAR-10 datasets
train_dataset = torchvision.datasets.CIFAR10(root='./data', train=True, download=True, transform=transform_train)
test_dataset = torchvision.datasets.CIFAR10(root='./data', train=False, download=True, transform=transform_test)

# Create data loaders
train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=128 * device_count, shuffle=True, num_workers=cpu_count)
test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=128 * device_count, shuffle=False, num_workers=cpu_count)

# Define the ResNet model
model = mobilenet_v3_small(pretrained=False, num_classes=10)
model = model.cuda()
# Check if there are multiple GPUs. If yes, then use DataParallel.
if torch.cuda.device_count() > 1:
  print("Let's use", torch.cuda.device_count(), "GPUs!")
  model = nn.DataParallel(model)

# Define the loss function and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(model.parameters(), lr=0.1, momentum=0.9, weight_decay=5e-4)

# Function to train the model
def train(epoch):
    model.train()
    train_loss = 0
    correct = 0
    total = 0
    for batch_idx, (inputs, targets) in enumerate(tqdm(train_loader)):
        inputs, targets = inputs.cuda(), targets.cuda()
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()

        train_loss += loss.item()
        _, predicted = outputs.max(1)
        total += targets.size(0)
        correct += predicted.eq(targets).sum().item()

    print(f'Train epoch: {epoch}, loss: {train_loss/total}, accuracy: {100.*correct/total}')

# Function to test the model
def test(epoch):
    model.eval()
    test_loss = 0
    correct = 0
    total = 0
    with torch.no_grad():
        for batch_idx, (inputs, targets) in enumerate(test_loader):
            inputs, targets = inputs.cuda(), targets.cuda()
            outputs = model(inputs)
            loss = criterion(outputs, targets)

            test_loss += loss.item()
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()

        print(f'Test epoch: {epoch}, loss: {test_loss/total}, accuracy: {100.*correct/total}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_train_epochs', type=int, default=1)
    args = parser.parse_args()

    # Training loop
    for epoch in range(args.num_train_epochs):
        train(epoch)
        test(epoch)
