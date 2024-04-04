# -*- coding: utf-8 -*-
"""M23CSA004_DLOps_ClassAssignment_2_Q_2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Uw-an28_iitonr_7tbrVKWbjCA7yWw1g
"""

import torch
import torchvision
import torchvision.transforms as transforms
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision.models import resnet101
import matplotlib.pyplot as plt

# Define transforms for the SVHN dataset
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

# Load SVHN dataset
train_dataset = torchvision.datasets.SVHN(root='./data', split='train', transform=transform, download=True)
test_dataset = torchvision.datasets.SVHN(root='./data', split='test', transform=transform, download=True)

# Define dataloaders
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True, num_workers=2)
test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False, num_workers=2)

# Load pre-trained ResNet101
resnet = resnet101(pretrained=True)
num_classes = 10  # SVHN has 10 classes

# Modify the last fully connected layer for fine-tuning
resnet.fc = nn.Linear(resnet.fc.in_features, num_classes)

# Move model to GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
resnet.to(device)

# Define loss function
criterion = nn.CrossEntropyLoss()

# Define optimizers
optimizers = {
    "Adam": optim.Adam(resnet.parameters(), lr=0.001),
    "Adagrad": optim.Adagrad(resnet.parameters(), lr=0.01),
    "RMSprop": optim.RMSprop(resnet.parameters(), lr=0.001)
}

# Training function
def train(optimizer, epochs=10):
    train_losses = []
    train_accuracies = []
    for epoch in range(epochs):
        running_loss = 0.0
        correct = 0
        total = 0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = resnet(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

        train_loss = running_loss / len(train_loader)
        train_accuracy = 100 * correct / total

        train_losses.append(train_loss)
        train_accuracies.append(train_accuracy)

        print(f"Epoch [{epoch+1}/{epochs}], Loss: {train_loss:.4f}, Accuracy: {train_accuracy:.2f}%")

    return train_losses, train_accuracies

# Training with each optimizer
results = {}
for optimizer_name, optimizer in optimizers.items():
    print(f"Training with {optimizer_name} optimizer...")
    train_losses, train_accuracies = train(optimizer)
    results[optimizer_name] = (train_losses, train_accuracies)

# Plotting training curves
plt.figure(figsize=(10, 5))
for optimizer_name, (train_losses, train_accuracies) in results.items():
    plt.plot(train_losses, label=f"{optimizer_name} Loss")
plt.xlabel("Epochs")
plt.ylabel("Training Loss")
plt.title("Training Loss Curves")
plt.legend()
plt.show()

plt.figure(figsize=(10, 5))
for optimizer_name, (train_losses, train_accuracies) in results.items():
    plt.plot(train_accuracies, label=f"{optimizer_name} Accuracy")
plt.xlabel("Epochs")
plt.ylabel("Training Accuracy (%)")
plt.title("Training Accuracy Curves")
plt.legend()
plt.show()

# Testing
def test():
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = resnet(images)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    print(f"Top-1 Test Accuracy: {100 * correct / total:.2f}%")
    top5_correct = 0
    for images, labels in test_loader:
        images, labels = images.to(device), labels.to(device)
        outputs = resnet(images)
        _, predicted = torch.topk(outputs, 5, dim=1)
        top5_correct += torch.sum(torch.sum(predicted == labels.view(-1, 1), dim=1) > 0).item()

    print(f"Top-5 Test Accuracy: {100 * top5_correct / total:.2f}%")

# Test the model
test()