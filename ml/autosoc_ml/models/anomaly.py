import torch
import torch.nn as nn

class AdvancedAutoencoder(nn.Module):
    """
    Phase 11 Advanced Autoencoder for Anomaly Detection.
    """
    def __init__(self, input_dim=7):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 16),
            nn.BatchNorm1d(16),
            nn.LeakyReLU(),
            nn.Linear(16, 8),
            nn.BatchNorm1d(8),
            nn.LeakyReLU(),
            nn.Linear(8, 4)
        )
        self.decoder = nn.Sequential(
            nn.Linear(4, 8),
            nn.BatchNorm1d(8),
            nn.LeakyReLU(),
            nn.Linear(8, 16),
            nn.BatchNorm1d(16),
            nn.LeakyReLU(),
            nn.Linear(16, input_dim)
        )
        
    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded
