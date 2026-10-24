import json
import os
import hashlib
import sys

MANIFESTS_DIR = os.path.join(os.path.dirname(__file__), "manifests")
RAW_DIR = os.path.join(os.path.dirname(__file__), "raw")

def verify_dataset(dataset_name):
    man_path = os.path.join(MANIFESTS_DIR, f"{dataset_name}.json")
    if not os.path.exists(man_path):
        print(f"Error: Manifest for {dataset_name} missing.")
        return False
        
    with open(man_path) as f:
        manifest = json.load(f)
        
    for fname, exp_chk in manifest.get("checksums", {}).items():
        fpath = os.path.join(RAW_DIR, dataset_name, fname)
        if not os.path.exists(fpath):
            print(f"Error: Data file {fpath} missing.")
            return False
            
        with open(fpath, "rb") as f_in:
            calc_chk = hashlib.sha256(f_in.read()).hexdigest()
            
        if calc_chk != exp_chk:
            print(f"Error: Checksum mismatch for {fpath}.")
            print(f"Expected: {exp_chk}")
            print(f"Got     : {calc_chk}")
            return False
            
    print(f"Success: {dataset_name} verified.")
    return True

if __name__ == "__main__":
    datasets = ["unsw_nb15", "cicids2017", "cic_iot_2023"]
    all_good = True
    for ds in datasets:
        if not verify_dataset(ds):
            all_good = False
            
    if not all_good:
        sys.exit(1)
    sys.exit(0)
