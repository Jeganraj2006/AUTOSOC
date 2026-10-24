"""
ml/autosoc_ml/progression/models/markov.py
Implements a first-order Markov Chain model for predicting the next ATT&CK technique.
"""
from typing import Dict, List, Tuple
from collections import defaultdict

class MarkovProgressionPredictor:
    def __init__(self):
        # transition_matrix[current_tech][next_tech] = count
        self.transition_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.state_totals: Dict[str, int] = defaultdict(int)
        self.global_prior: Dict[str, float] = {}

    def fit(self, sequences: List[List[str]]):
        """
        Trains the Markov model from a list of sequences of technique IDs.
        """
        global_counts = defaultdict(int)
        total_transitions = 0

        for seq in sequences:
            for i in range(len(seq) - 1):
                curr_t = seq[i]
                next_t = seq[i + 1]
                self.transition_counts[curr_t][next_t] += 1
                self.state_totals[curr_t] += 1
                global_counts[next_t] += 1
                total_transitions += 1
                
            if seq:
                global_counts[seq[-1]] += 1
                total_transitions += 1

        # Calculate global prior for fallback
        for t, count in global_counts.items():
            self.global_prior[t] = count / total_transitions if total_transitions > 0 else 0.0

    def predict(self, current_technique: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        Predicts the next top_k techniques given the current technique.
        Returns a list of (technique_id, probability) sorted by probability.
        """
        if current_technique not in self.transition_counts or self.state_totals[current_technique] == 0:
            # Fallback to global prior
            sorted_prior = sorted(self.global_prior.items(), key=lambda x: x[1], reverse=True)
            return sorted_prior[:top_k]

        counts = self.transition_counts[current_technique]
        total = self.state_totals[current_technique]
        
        probs = [(t, count / total) for t, count in counts.items()]
        probs.sort(key=lambda x: x[1], reverse=True)
        return probs[:top_k]
