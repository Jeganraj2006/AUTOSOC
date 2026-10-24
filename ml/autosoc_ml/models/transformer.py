import torch
import torch.nn as nn

class TransformerDetector(nn.Module):
    """
    Compact Transformer Encoder for event sequences.
    """
    def __init__(self, feature_dim=7, d_model=16, nhead=2, num_layers=1, out_classes=1):
        super().__init__()
        self.input_projection = nn.Linear(feature_dim, d_model)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, 
            nhead=nhead, 
            dim_feedforward=32,
            dropout=0.1,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        self.fc = nn.Linear(d_model, out_classes)
        
    def forward(self, x):
        # x: (batch_size, seq_len, feature_dim)
        proj = self.input_projection(x)
        
        encoded = self.transformer(proj)
        
        # Average pooling across sequence length
        pooled = encoded.mean(dim=1)
        
        logits = self.fc(pooled)
        return torch.sigmoid(logits)
