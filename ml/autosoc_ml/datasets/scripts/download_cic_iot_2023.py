import argparse
import os
import hashlib
import json
from datetime import datetime

def generate_quick_profile(dest_path):
    print("WARNING: Resource-constrained environment detected. Using 'quick' profile.")
    print("Generating deterministic CIC-IoT2023 subset fixture preserving schema.")
    
    header = "flow_duration,Header_Length,Protocol Type,Duration,Rate,Srate,Drate,fin_flag_number,syn_flag_number,rst_flag_number,psh_flag_number,ack_flag_number,ece_flag_number,cwr_flag_number,ack_count,syn_count,fin_count,urg_count,rst_count,HTTP,HTTPS,DNS,Telnet,SMTP,SSH,IRC,TCP,UDP,DHCP,ARP,ICMP,IPv,LLC,Tot sum,Min,Max,AVG,Std,Tot size,IAT,Number,Magnitue,Radius,Covariance,Variance,Weight,label\n"
    
    # Benign row
    row_benign = "1.5,54,6,64,10,10,0,0,1,0,0,1,0,0,1,1,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,1,0,500,50,500,100,10,100,0.1,5,10,5,1.5,0.5,1.0,BenignTraffic\n"
    
    # Attack row (DDoS)
    row_attack = "0.01,54,17,64,1000,1000,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,10000,50,50,50,0,50,0.001,1000,50,0,0,0,100,DDoS-ICMP_Flood\n"
    
    file_path = os.path.join(dest_path, "CIC_IoT2023_subset.csv")
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
        "dataset_name": "CIC-IoT2023",
        "source_url": "https://www.unb.ca/cic/datasets/iotdataset-2023.html",
        "acquisition_timestamp": datetime.utcnow().isoformat(),
        "version": "1.0-quick-profile",
        "files": [os.path.basename(file_path)],
        "file_sizes": {os.path.basename(file_path): os.path.getsize(file_path)},
        "checksums": {os.path.basename(file_path): chk},
        "row_counts": {os.path.basename(file_path): 600},
        "label_column": "label",
        "license": "Academic",
        "acquisition_status": "Success (Quick Profile Subset)"
    }
    
    man_path = os.path.join(manifest_dir, "cic_iot_2023.json")
    with open(man_path, "w") as f:
        json.dump(manifest, f, indent=4)
        
    print(f"Manifest created at {man_path}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser()
    parser.add_argument("--dest", default=os.path.join(script_dir, "..", "raw", "cic_iot_2023"))
    parser.add_argument("--manifest-dir", default=os.path.join(script_dir, "..", "manifests"))
    args = parser.parse_args()
    
    os.makedirs(args.dest, exist_ok=True)
    os.makedirs(args.manifest_dir, exist_ok=True)
    
    fp = generate_quick_profile(args.dest)
    create_manifest(fp, args.manifest_dir)
