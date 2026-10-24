import torch
import torch.nn as nn
import torch.nn.functional as F

class CnnDetector(nn.Module):
    """
    1D CNN processing temporal features.
    Expected Input Shape: (batch_size, channels=feature_dim, seq_len)
    """
    def __init__(self, feature_dim=7, seq_len=5, out_classes=1):
        super().__init__()
        # Ensure we have at least one valid conv configuration
        self.conv1 = nn.Conv1d(in_channels=feature_dim, out_channels=16, kernel_size=1)
        self.bn1 = nn.BatchNorm1d(16)
        
        self.conv2 = nn.Conv1d(in_channels=16, out_channels=32, kernel_size=1)
        self.bn2 = nn.BatchNorm1d(32)
        
        self.dropout = nn.Dropout(0.3)
        self.fc1 = nn.Linear(32 * seq_len, 16)
        self.fc2 = nn.Linear(16, out_classes)
        
    def forward(self, x):
        # x is (batch_size, seq_len, feature_dim) -> transpose for Conv1d
        x = x.transpose(1, 2)
        
        x = F.relu(self.bn1(self.conv1(x)))
        x = self.dropout(x)
        x = F.relu(self.bn2(self.conv2(x)))
        
        # Flatten
        x = x.view(x.size(0), -1)
        
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        logits = self.fc2(x)
        return torch.sigmoid(logits)
