import numpy as np
import collections

class SequenceBuilder:
    """
    Constructs bounded temporal sequences for deep learning models (LSTM, Transformer).
    In production, this buffers events grouped by an entity key (e.g., source IP).
    In offline training with strictly independent flow datasets lacking entity IDs,
    this yields sequences of length 1 to prevent arbitrary mixing of unrelated flows.
    """
    def __init__(self, max_seq_len=5, feature_dim=7):
        self.max_seq_len = max_seq_len
        self.feature_dim = feature_dim
        self._buffers = collections.defaultdict(lambda: collections.deque(maxlen=max_seq_len))
        
    def add_event(self, entity_key: str, feature_vector: np.ndarray):
        """
        Adds a preprocessed feature vector to the entity's buffer.
        """
        if len(feature_vector) != self.feature_dim:
            raise ValueError(f"Expected feature_dim={self.feature_dim}, got {len(feature_vector)}")
        self._buffers[entity_key].append(feature_vector)
        
    def get_sequence(self, entity_key: str) -> np.ndarray:
        """
        Returns the padded sequence for the entity. Shape: (max_seq_len, feature_dim).
        The most recent event is at the end of the sequence.
        Missing early steps are zero-padded.
        """
        buffer = self._buffers[entity_key]
        seq = np.zeros((self.max_seq_len, self.feature_dim), dtype=np.float32)
        
        if len(buffer) > 0:
            events = np.array(buffer, dtype=np.float32)
            # Place at the end of the sequence (right-aligned)
            seq[-len(buffer):, :] = events
            
        return seq

    def build_from_dataframe(self, df) -> np.ndarray:
        """
        For Phase 10 CSVs that lack entity identifiers (to prevent leakage), 
        we cannot arbitrarily mix independent flows into sequences.
        Therefore, we treat each row as an independent sequence of length 1,
        padded to max_seq_len.
        
        Input: DataFrame shape (N, feature_dim)
        Output: Sequence shape (N, max_seq_len, feature_dim)
        """
        features = df.values.astype(np.float32)
        N = features.shape[0]
        
        # Initialize zero-padded sequences
        sequences = np.zeros((N, self.max_seq_len, self.feature_dim), dtype=np.float32)
        
        # Place the single event at the last time step
        sequences[:, -1, :] = features
        
        return sequences
