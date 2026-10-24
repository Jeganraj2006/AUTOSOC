import argparse
import random
import time
import json
import uuid
from datetime import datetime, timezone

def generate_events(count: int, source_id: str, seed: int = None):
    if seed is not None:
        random.seed(seed)
        
    event_types = ["login", "failed_login", "process_execution", "network_connection"]
    
    events = []
    for _ in range(count):
        evt_type = random.choice(event_types)
        
        event = {
            "synthetic_id": str(uuid.uuid4()),
            "type": evt_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_ip": f"10.0.{random.randint(1, 255)}.{random.randint(1, 255)}",
            "user": f"user_{random.randint(1, 100)}",
            "message": f"Synthetic {evt_type} event generated for testing."
        }
        
        if evt_type == "process_execution":
            event["process"] = random.choice(["cmd.exe", "powershell.exe", "bash", "python"])
        elif evt_type == "network_connection":
            event["destination_port"] = random.choice([80, 443, 22, 3389])
            
        events.append(json.dumps(event))
    return events

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic security events")
    parser.add_argument("--count", type=int, default=10, help="Number of events to generate")
    parser.add_argument("--rate", type=float, default=0.0, help="Events per second (0 for batch)")
    parser.add_argument("--source-id", required=True, help="DataSource ID")
    parser.add_argument("--seed", type=int, help="Random seed")
    parser.add_argument("--output", type=str, help="Output file path (prints to stdout if omitted)")
    
    args = parser.parse_args()
    
    generated = generate_events(args.count, args.source_id, args.seed)
    
    if args.output:
        with open(args.output, "w") as f:
            if args.rate > 0:
                for evt in generated:
                    f.write(evt + "\n")
                    f.flush()
                    time.sleep(1.0 / args.rate)
            else:
                for evt in generated:
                    f.write(evt + "\n")
    else:
        for evt in generated:
            print(evt)
            if args.rate > 0:
                time.sleep(1.0 / args.rate)
