# Common ML Feature Contract

This document outlines the standard subset of features extracted across different datasets (UNSW-NB15, CICIDS2017, CIC-IoT2023) to enable common models and cross-dataset evaluation.

## Selected Features
1. **duration**: The flow duration in seconds.
   - *Type*: numeric
   - *Missing Value Policy*: Impute median
2. **proto_tcp**: Indicator if protocol is TCP.
   - *Type*: numeric (0/1)
3. **proto_udp**: Indicator if protocol is UDP.
   - *Type*: numeric (0/1)
4. **fwd_pkts**: Total forward packets.
   - *Type*: numeric
5. **bwd_pkts**: Total backward packets.
   - *Type*: numeric
6. **fwd_bytes**: Total forward bytes.
   - *Type*: numeric
7. **bwd_bytes**: Total backward bytes.
   - *Type*: numeric
8. **label**: Target class mapping to `benign` or `attack`.
   - *Type*: categorical

## Rationale
These features are typically universally present or derivable from both flow-based packet captures and streaming ingestion sources (like Zeek or NetFlow) used in AutoSOC.
