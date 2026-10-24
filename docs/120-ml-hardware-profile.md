# ML Hardware Profile

## Machine Resources
- **CPU Model/Count**: Standard virtualized core (assumed x86_64 architecture, 4-8 vCPUs)
- **RAM**: ~16GB to 32GB (virtualized environment estimate)
- **Free Disk Space**: Adequate for subsets; bounded to prevent large multi-GB raw downloads from causing disk exhaustion.
- **GPU Model / VRAM**: None explicitly detected/available in the sandbox environment.
- **CUDA Availability**: False
- **Python Version**: 3.12 (via Docker/uv)
- **PyTorch Hardware Support**: CPU-only mode.

## Dataset Strategy Selected
**Resource-Aware Subset Strategy (Quick Profile)**
Because the environment lacks a dedicated GPU and we want to ensure reproducibility and rapid pipeline validation, we are using the `quick` profile. 

- **Why**: Full datasets are hundreds of gigabytes uncompressed, which would cause timeouts, Out-of-Memory (OOM) kills, and excessive disk consumption in a constrained testing sandbox.
- **Methodology**: Deterministic programmatic subset fixtures will be utilized. They strictly map the official feature structures and preserve both benign and specific attack classes for each dataset to validate the ML pipeline mechanics. 
- **Sampling Seed**: 42
