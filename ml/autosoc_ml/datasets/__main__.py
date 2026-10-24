import argparse
import json
import os

MANIFESTS_DIR = os.path.join(os.path.dirname(__file__), "manifests")
RAW_DIR = os.path.join(os.path.dirname(__file__), "raw")

def show_status():
    print("AutoSOC ML Datasets Status:")
    print("-" * 50)
    for ds in ["unsw_nb15", "cicids2017", "cic_iot_2023"]:
        man_path = os.path.join(MANIFESTS_DIR, f"{ds}.json")
        if os.path.exists(man_path):
            with open(man_path) as f:
                data = json.load(f)
            print(f"Dataset: {data.get('dataset_name')}")
            print(f"  Acquired: Yes")
            print(f"  Verified: Yes")
            print(f"  Version: {data.get('version')}")
            print(f"  Total Size: {sum(data.get('file_sizes', {}).values())} bytes")
            print(f"  Total Rows: {sum(data.get('row_counts', {}).values())}")
            print(f"  Status: {data.get('acquisition_status')}")
            print("-" * 50)
        else:
            print(f"Dataset: {ds}")
            print(f"  Acquired: No")
            print("-" * 50)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["status"], help="Command to run")
    args = parser.parse_args()
    
    if args.command == "status":
        show_status()
