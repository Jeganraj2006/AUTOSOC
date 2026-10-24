"""
ml/autosoc_ml/progression/training/loop.py
Training loop for PyTorch sequence predictors with early stopping and MLflow logging.
"""
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import numpy as np

def compute_metrics(logits: torch.Tensor, targets: torch.Tensor):
    """
    Computes Top-1 and Top-3 accuracy for the batch.
    logits: (batch, vocab_size)
    targets: (batch)
    """
    with torch.no_grad():
        _, top3_preds = logits.topk(3, dim=-1)
        top1_preds = top3_preds[:, 0]
        
        top1_acc = (top1_preds == targets).float().mean().item()
        
        top3_acc = 0.0
        for i in range(targets.size(0)):
            if targets[i] in top3_preds[i]:
                top3_acc += 1
        top3_acc = top3_acc / targets.size(0) if targets.size(0) > 0 else 0.0
        
        return top1_acc, top3_acc

def train_epoch(model: nn.Module, dataloader: DataLoader, optimizer: torch.optim.Optimizer, criterion: nn.Module, device: torch.device):
    model.train()
    total_loss = 0.0
    total_top1 = 0.0
    total_top3 = 0.0
    batches = 0
    
    for inputs, targets in dataloader:
        inputs, targets = inputs.to(device), targets.to(device)
        
        optimizer.zero_grad()
        
        # Determine if it's LSTM or Transformer and pass appropriate kwargs
        logits = model(inputs)
        
        # Flatten logits and targets for CrossEntropyLoss
        # Usually sequences are predicted per step, so we might need to reshape
        if logits.dim() == 3:
            logits = logits.view(-1, logits.size(-1))
            targets = targets.view(-1)
            
        loss = criterion(logits, targets)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        top1, top3 = compute_metrics(logits, targets)
        total_top1 += top1
        total_top3 += top3
        batches += 1
        
    return total_loss / batches, total_top1 / batches, total_top3 / batches

def validate_epoch(model: nn.Module, dataloader: DataLoader, criterion: nn.Module, device: torch.device):
    model.eval()
    total_loss = 0.0
    total_top1 = 0.0
    total_top3 = 0.0
    batches = 0
    
    with torch.no_grad():
        for inputs, targets in dataloader:
            inputs, targets = inputs.to(device), targets.to(device)
            
            logits = model(inputs)
            
            if logits.dim() == 3:
                logits = logits.view(-1, logits.size(-1))
                targets = targets.view(-1)
                
            loss = criterion(logits, targets)
            
            total_loss += loss.item()
            top1, top3 = compute_metrics(logits, targets)
            total_top1 += top1
            total_top3 += top3
            batches += 1
            
    return total_loss / batches, total_top1 / batches, total_top3 / batches
