"""
ml/autosoc_ml/progression/models/lstm.py
Implements an LSTM sequence predictor for ATT&CK techniques.
"""
import torch
import torch.nn as nn
from typing import Dict, Any

class LSTMProgressionModel(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        embedding_dim: int = 128,
        hidden_dim: int = 256,
        num_layers: int = 2,
        dropout: float = 0.3
    ):
        super().__init__()
        self.vocab_size = vocab_size
        self.embedding = nn.Embedding(num_embeddings=vocab_size, embedding_dim=embedding_dim, padding_idx=0)
        
        self.lstm = nn.LSTM(
            input_size=embedding_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0
        )
        
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(hidden_dim, vocab_size)
        
    def forward(self, x: torch.Tensor, lengths: torch.Tensor = None) -> torch.Tensor:
        """
        x: (batch_size, seq_len)
        Returns logits of shape (batch_size, seq_len, vocab_size)
        """
        embedded = self.embedding(x)
        embedded = self.dropout(embedded)
        
        # If lengths are provided, we could pack_padded_sequence here for efficiency.
        # For simplicity in this baseline, we'll process padded sequences directly.
        lstm_out, _ = self.lstm(embedded)
        
        lstm_out = self.dropout(lstm_out)
        logits = self.classifier(lstm_out)
        
        return logits
    
    def predict_next(self, x: torch.Tensor) -> torch.Tensor:
        """
        Predicts the next token for a single sequence or batch.
        Returns probabilities of shape (batch_size, vocab_size)
        """
        self.eval()
        with torch.no_grad():
            logits = self.forward(x)
            # Take the output from the last timestep
            last_logits = logits[:, -1, :]
            probs = torch.softmax(last_logits, dim=-1)
        return probs
