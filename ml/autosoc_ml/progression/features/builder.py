"""
ml/autosoc_ml/progression/features/builder.py
Builds technique sequences and extracts graph context from incident mappings.
"""
from typing import List, Dict, Any, Optional
import json

class ProgressionFeatureBuilder:
    def __init__(self, vocab_path: str = None):
        self.vocab = {}
        if vocab_path:
            with open(vocab_path, "r") as f:
                self.vocab = json.load(f)
                
        # If vocab is empty, use dynamic creation during building
        self.unk_token = self.vocab.get("<UNK>", 1)
        self.pad_token = self.vocab.get("<PAD>", 0)

    def extract_sequence(self, incident_mappings: List[Dict[str, Any]]) -> List[str]:
        """
        Extracts ordered list of technique IDs from incident mappings.
        Sorts by timestamp.
        Filters out 'rejected' mappings.
        """
        valid_mappings = [m for m in incident_mappings if m.get("status") != "rejected"]
        
        # Sort by mapped_at or created_at
        valid_mappings.sort(key=lambda x: x.get("mapped_at") or x.get("created_at") or "")
        
        sequence = [m["technique_id"] for m in valid_mappings if "technique_id" in m]
        return sequence

    def encode_sequence(self, sequence: List[str]) -> List[int]:
        """
        Converts list of technique strings to integer tokens using vocabulary.
        """
        return [self.vocab.get(tech, self.unk_token) for tech in sequence]

    def extract_graph_features(self, incident: Dict[str, Any], current_time: str = None) -> Dict[str, Any]:
        """
        Extracts graph context without temporal leakage.
        (Only features available up to `current_time`)
        """
        # Placeholder for graph feature extraction MVP
        # - node counts
        # - degree of primary entities
        return {
            "node_count": 0,
            "user_count": 0,
            "host_count": 0
        }
