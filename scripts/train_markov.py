import os
import json

from autosoc_ml.progression.models.markov import MarkovProgressionPredictor


SEQUENCES = [
    ["T1566", "T1059.001", "T1078", "T1110", "T1021.002"],
    ["T1566", "T1059.001", "T1078", "T1105", "T1021.002"],
    ["T1059.001", "T1078", "T1110", "T1021.002"],
    ["T1059.001", "T1078", "T1105", "T1021.002"],
    ["T1059.001", "T1078", "T1105", "T1047"],
    ["T1078", "T1110", "T1059.001", "T1105"],
    ["T1566", "T1059.001", "T1078", "T1105"],
    ["T1059.001", "T1078", "T1110"],
    ["T1078", "T1105", "T1021.002"],
    ["T1110", "T1059.001", "T1078"],
]


MODEL_DIR = os.path.join(os.getcwd(), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "markov_model.json")

os.makedirs(MODEL_DIR, exist_ok=True)

print("Training Markov progression model...")

model = MarkovProgressionPredictor()
model.fit(SEQUENCES)

# Convert defaultdict structures into normal dictionaries
transition_counts = {
    current: dict(transitions)
    for current, transitions in model.transition_counts.items()
}

trained_model = {
    "transition_counts": transition_counts,
    "state_totals": dict(model.state_totals),
    "global_prior": model.global_prior,
}

with open(MODEL_PATH, "w") as f:
    json.dump(trained_model, f, indent=2)

print("Training completed.")
print(f"Training sequences: {len(SEQUENCES)}")
print(f"Model saved to: {MODEL_PATH}")

print("\nLearned transitions:")

for current, transitions in transition_counts.items():
    print(f"\n{current} ->")

    for next_technique, count in transitions.items():
        print(f"    {next_technique}: {count}")

print("\nTest prediction:")
print("T1059.001 ->", model.predict("T1059.001", top_k=3))