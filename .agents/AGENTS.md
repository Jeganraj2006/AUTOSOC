# ML Training Rules

1. **Hardware Acceleration Requirement**: Moving forward, any local machine learning training MUST utilize the system's local GPU (e.g., CUDA in PyTorch or RAPIDS for Scikit-Learn if available). 
2. **Google Colab Priority**: If local GPU training is unfeasible or unsupported by the current framework versions, offload the training process to Google Colab. Do not default to CPU-only training for future workloads.
