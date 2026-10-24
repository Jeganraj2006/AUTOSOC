"""
ml/autosoc_ml/progression/models/transformer.py
Implements a Transformer sequence predictor for ATT&CK techniques.
"""
import math
import torch
import torch.nn as nn

class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, dropout: float = 0.1, max_len: int = 5000):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)

        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))
        pe = torch.zeros(1, max_len, d_model)
        pe[0, :, 0::2] = torch.sin(position * div_term)
        pe[0, :, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Tensor, shape [batch_size, seq_len, embedding_dim]
        """
        x = x + self.pe[:, :x.size(1), :]
        return self.dropout(x)


class TransformerProgressionModel(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        embedding_dim: int = 128,
        num_heads: int = 4,
        hidden_dim: int = 256,
        num_layers: int = 2,
        dropout: float = 0.3
    ):
        super().__init__()
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        
        self.embedding = nn.Embedding(num_embeddings=vocab_size, embedding_dim=embedding_dim, padding_idx=0)
        self.pos_encoder = PositionalEncoding(embedding_dim, dropout)
        
        encoder_layers = nn.TransformerEncoderLayer(
            d_model=embedding_dim,
            nhead=num_heads,
            dim_feedforward=hidden_dim,
            dropout=dropout,
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layers, num_layers=num_layers)
        
        self.classifier = nn.Linear(embedding_dim, vocab_size)
        
    def generate_square_subsequent_mask(self, sz: int) -> torch.Tensor:
        """
        Generates an upper-triangular matrix of -inf, with zeros on diag.
        Ensures the model can only look at past tokens.
        """
        mask = (torch.triu(torch.ones(sz, sz)) == 1).transpose(0, 1)
        mask = mask.float().masked_fill(mask == 0, float('-inf')).masked_fill(mask == 1, float(0.0))
        return mask

    def forward(self, x: torch.Tensor, pad_mask: torch.Tensor = None) -> torch.Tensor:
        """
        x: (batch_size, seq_len)
        pad_mask: (batch_size, seq_len) boolean mask where True means padding.
        Returns logits of shape (batch_size, seq_len, vocab_size)
        """
        seq_len = x.size(1)
        causal_mask = self.generate_square_subsequent_mask(seq_len).to(x.device)
        
        embedded = self.embedding(x) * math.sqrt(self.embedding_dim)
        embedded = self.pos_encoder(embedded)
        
        # transformer_encoder requires src_key_padding_mask where True = ignore
        output = self.transformer_encoder(
            embedded,
            mask=causal_mask,
            src_key_padding_mask=pad_mask
        )
        
        logits = self.classifier(output)
        return logits
    
    def predict_next(self, x: torch.Tensor, pad_mask: torch.Tensor = None) -> torch.Tensor:
        self.eval()
        with torch.no_grad():
            logits = self.forward(x, pad_mask)
            last_logits = logits[:, -1, :]
            probs = torch.softmax(last_logits, dim=-1)
        return probs
