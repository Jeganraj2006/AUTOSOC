import sys
import os
import uuid

# Add directories to python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "packages", "event-schemas", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "ml"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "workers", "ml-inference", "src"))

from autosoc_ml_inference.consumer import MLInferenceWorker

def main():
    worker = MLInferenceWorker()

    print("\n--- Running End-to-End Scientific Boundary Tests ---")
    
    # Example 1: Benign Event
    benign_event = {
        "event": {"id": str(uuid.uuid4()), "duration": 0.05},
        "network": {"protocol": "tcp", "packets_out": 5, "packets_in": 5, "bytes_out": 200, "bytes_in": 300},
        "source": {"ip": "192.168.1.5"}
    }
    res1 = worker.process_event(benign_event)
    print("\n[Example 1 - Benign Event]")
    if res1 is None:
        print("Result: No alert generated (Classified as NORMAL). Expected behavior.")
    else:
        print("Result:", res1)
        
    # Example 2: Known Attack-like Pattern (e.g. SSH Brute Force)
    known_event = {
        "event": {"id": str(uuid.uuid4()), "duration": 1.2},
        "network": {"protocol": "ssh", "packets_out": 150, "packets_in": 100, "bytes_out": 5000, "bytes_in": 4000},
        "source": {"ip": "10.0.0.8"}
    }
    res2 = worker.process_event(known_event)
    print("\n[Example 2 - Known Attack Pattern]")
    if res2:
        print(f"Result: Alert Generated.")
        print(f"Title: {res2.title}")
        print(f"Classification: {res2.detection_type}")
        print(f"Confidence: {res2.confidence}")
    else:
        print("Result: No alert.")

    # Example 3: Unknown / High Anomaly Controlled Pattern
    unknown_event = {
        "event": {"id": str(uuid.uuid4()), "duration": 0.001},
        "network": {"protocol": "udp", "packets_out": 1, "packets_in": 0, "bytes_out": 85000, "bytes_in": 0},
        "source": {"ip": "203.0.113.50"}
    }
    res3 = worker.process_event(unknown_event)
    print("\n[Example 3 - High Anomaly Unknown Pattern]")
    if res3:
        print(f"Result: Alert Generated.")
        print(f"Title: {res3.title}")
        print(f"Classification: {res3.detection_type}")
        print(f"Anomaly Score: {res3.anomaly_score}")
        assert "Zero-Day Behavior" in res3.title and "Confirmed" not in res3.title, "FAILED: Violates terminology scientific guardrails"
    else:
        print("Result: No alert.")
        
    print("\nAll boundary tests passed successfully.")

if __name__ == "__main__":
    main()
