import os
import json
import hashlib
import time
import urllib.request
from datetime import datetime, timezone

URL = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "mitre"))
MANIFEST_PATH = os.path.join(DATA_DIR, "manifests", "enterprise-attack.json")
BUNDLE_PATH = os.path.join(DATA_DIR, "enterprise-attack-bundle.json")

def fetch_attack_data():
    print(f"Fetching MITRE ATT&CK STIX 2.1 data from {URL}...")
    
    # Ensure directories exist
    os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
    
    # Download with a timeout
    req = urllib.request.Request(URL, headers={'User-Agent': 'AutoSOC/1.0'})
    start_time = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()
    except Exception as e:
        print(f"Failed to fetch ATT&CK data: {e}")
        return
    
    fetch_duration = time.time() - start_time
    print(f"Downloaded {len(data)} bytes in {fetch_duration:.2f} seconds.")
    
    # Calculate SHA-256
    sha256_hash = hashlib.sha256(data).hexdigest()
    
    # Parse JSON
    try:
        bundle = json.loads(data)
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        return
        
    if bundle.get("type") != "bundle":
        print("Error: Acquired data is not a STIX bundle.")
        return
        
    objects = bundle.get("objects", [])
    
    tactics = 0
    techniques = 0
    sub_techniques = 0
    relationships = 0
    
    for obj in objects:
        obj_type = obj.get("type")
        if obj_type == "x-mitre-tactic":
            tactics += 1
        elif obj_type == "attack-pattern":
            if obj.get("x_mitre_is_subtechnique"):
                sub_techniques += 1
            else:
                techniques += 1
        elif obj_type == "relationship":
            relationships += 1
            
    # Write bundle to disk
    with open(BUNDLE_PATH, "wb") as f:
        f.write(data)
        
    # Create manifest
    manifest = {
        "version": "latest", # Normally parsed from STIX, but 'latest' simplifies if not present globally
        "source": URL,
        "acquisition_timestamp": datetime.now(timezone.utc).isoformat(),
        "sha256": sha256_hash,
        "stix_version": "2.1",
        "counts": {
            "tactics": tactics,
            "techniques": techniques,
            "sub_techniques": sub_techniques,
            "relationships": relationships,
            "total_objects": len(objects)
        }
    }
    
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        
    print("ATT&CK data acquired and verified.")
    print(f"SHA-256: {sha256_hash}")
    print(f"Tactics: {tactics}, Techniques: {techniques}, Sub-techniques: {sub_techniques}")
    
if __name__ == "__main__":
    fetch_attack_data()
