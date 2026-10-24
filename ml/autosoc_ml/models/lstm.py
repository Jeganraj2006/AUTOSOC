import torch
import torch.nn as nn

class LstmDetector(nn.Module):
    """
    LSTM processing sequence of events.
    Expected Input Shape: (batch_size, seq_len, feature_dim)
    """
    def __init__(self, feature_dim=7, hidden_size=32, num_layers=1, out_classes=1):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=feature_dim, 
            hidden_size=hidden_size, 
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2 if num_layers > 1 else 0.0
        )
        self.dropout = nn.Dropout(0.3)
        self.fc = nn.Linear(hidden_size, out_classes)
        
    def forward(self, x):
        # x: (batch_size, seq_len, feature_dim)
        lstm_out, (hn, cn) = self.lstm(x)
        
        # Take the last sequence step
        last_out = lstm_out[:, -1, :]
        last_out = self.dropout(last_out)
        
        logits = self.fc(last_out)
        return torch.sigmoid(logits)
