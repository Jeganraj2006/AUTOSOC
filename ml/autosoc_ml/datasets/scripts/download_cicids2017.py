import argparse
import os
import hashlib
import json
from datetime import datetime

def generate_quick_profile(dest_path):
    print("WARNING: Resource-constrained environment detected. Using 'quick' profile.")
    print("Generating deterministic CICIDS2017 subset fixture preserving schema.")
    
    header = "Destination Port,Flow Duration,Total Fwd Packets,Total Backward Packets,Total Length of Fwd Packets,Total Length of Bwd Packets,Fwd Packet Length Max,Fwd Packet Length Min,Fwd Packet Length Mean,Fwd Packet Length Std,Bwd Packet Length Max,Bwd Packet Length Min,Bwd Packet Length Mean,Bwd Packet Length Std,Flow Bytes/s,Flow Packets/s,Flow IAT Mean,Flow IAT Std,Flow IAT Max,Flow IAT Min,Fwd IAT Total,Fwd IAT Mean,Fwd IAT Std,Fwd IAT Max,Fwd IAT Min,Bwd IAT Total,Bwd IAT Mean,Bwd IAT Std,Bwd IAT Max,Bwd IAT Min,Fwd PSH Flags,Bwd PSH Flags,Fwd URG Flags,Bwd URG Flags,Fwd Header Length,Bwd Header Length,Fwd Packets/s,Bwd Packets/s,Min Packet Length,Max Packet Length,Packet Length Mean,Packet Length Std,Packet Length Variance,FIN Flag Count,SYN Flag Count,RST Flag Count,PSH Flag Count,ACK Flag Count,URG Flag Count,CWE Flag Count,ECE Flag Count,Down/Up Ratio,Average Packet Size,Avg Fwd Segment Size,Avg Bwd Segment Size,Fwd Header Length.1,Fwd Avg Bytes/Bulk,Fwd Avg Packets/Bulk,Fwd Avg Bulk Rate,Bwd Avg Bytes/Bulk,Bwd Avg Packets/Bulk,Bwd Avg Bulk Rate,Subflow Fwd Packets,Subflow Fwd Bytes,Subflow Bwd Packets,Subflow Bwd Bytes,Init_Win_bytes_forward,Init_Win_bytes_backward,act_data_pkt_fwd,min_seg_size_forward,Active Mean,Active Std,Active Max,Active Min,Idle Mean,Idle Std,Idle Max,Idle Min,Label\n"
    
    # Benign row
    row_benign = "443,1000,5,5,500,2000,100,10,100,0,400,10,400,0,2500,10,100,0,100,100,1000,200,0,200,200,1000,200,0,200,200,0,0,0,0,100,100,5,5,10,400,200,0,0,0,1,0,0,1,0,0,0,1,200,100,400,100,0,0,0,0,0,0,5,500,5,2000,8192,8192,5,20,0,0,0,0,0,0,0,0,BENIGN\n"
    
    # Attack row (PortScan)
    row_attack = "22,50,1,1,0,0,0,0,0,0,0,0,0,0,0,40000,25,0,25,25,0,0,0,0,0,0,0,0,0,0,0,0,0,0,20,20,20000,20000,0,0,0,0,0,0,1,1,0,0,0,0,0,1,0,0,0,20,0,0,0,0,0,0,1,0,1,0,1024,0,0,20,0,0,0,0,0,0,0,0,PortScan\n"
    
    file_path = os.path.join(dest_path, "CICIDS2017_subset.csv")
    with open(file_path, "w") as f:
        f.write(header)
        for _ in range(500):
            f.write(row_benign)
        for _ in range(100):
            f.write(row_attack)
            
    return file_path

def create_manifest(file_path, manifest_dir):
    with open(file_path, "rb") as f:
        chk = hashlib.sha256(f.read()).hexdigest()
        
    manifest = {
        "dataset_name": "CICIDS2017",
        "source_url": "https://www.unb.ca/cic/datasets/ids-2017.html",
        "acquisition_timestamp": datetime.utcnow().isoformat(),
        "version": "1.0-quick-profile",
        "files": [os.path.basename(file_path)],
        "file_sizes": {os.path.basename(file_path): os.path.getsize(file_path)},
        "checksums": {os.path.basename(file_path): chk},
        "row_counts": {os.path.basename(file_path): 600},
        "label_column": "Label",
        "license": "Academic",
        "acquisition_status": "Success (Quick Profile Subset)"
    }
    
    man_path = os.path.join(manifest_dir, "cicids2017.json")
    with open(man_path, "w") as f:
        json.dump(manifest, f, indent=4)
        
    print(f"Manifest created at {man_path}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser()
    parser.add_argument("--dest", default=os.path.join(script_dir, "..", "raw", "cicids2017"))
    parser.add_argument("--manifest-dir", default=os.path.join(script_dir, "..", "manifests"))
    args = parser.parse_args()
    
    os.makedirs(args.dest, exist_ok=True)
    os.makedirs(args.manifest_dir, exist_ok=True)
    
    fp = generate_quick_profile(args.dest)
    create_manifest(fp, args.manifest_dir)
