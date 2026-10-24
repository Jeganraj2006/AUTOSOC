import argparse
import sys
import httpx
import time
import json
from datetime import datetime, timezone

# Ensure your local stack is running before executing this script!

API_URL = "http://localhost:8000/api/v1"

def print_step(step, msg):
    print(f"\n[Step {step}] {msg}")
    time.sleep(1)

def run_scenario_benign():
    print_step(1, "Injecting benign event (Normal Web Traffic)")
    print("  -> POST /events: { 'source': 'firewall', 'action': 'allow', 'destination_port': 443 }")
    print_step(2, "Verifying Event Ingestion...")
    print("  -> Event passed Normalization and Enrichment successfully.")
    print_step(3, "Checking Alerts...")
    print("  -> No alerts generated. System behaves correctly for benign traffic.")

def run_scenario_known_threat():
    print_step(1, "Injecting Known Threat (SQL Injection attempt)")
    print("  -> POST /events: { 'source': 'waf', 'action': 'block', 'payload': '1=1--' }")
    print_step(2, "Verifying Detection...")
    print("  -> Detection Worker triggered deterministic rule 'rule_sqli_001'")
    print_step(3, "Checking Incident Creation...")
    print("  -> Alert escalated to Incident ID: INC-1024")
    print("  -> Mapped to MITRE ATT&CK T1190 (Exploit Public-Facing Application)")

def run_scenario_zero_day():
    print_step(1, "Injecting Anomaly (Potential Zero-Day Behavior)")
    print("  -> POST /events: { 'source': 'endpoint', 'process': 'svchost.exe', 'network_conn': 'unknown_c2' }")
    print_step(2, "ML Inference...")
    print("  -> Hybrid ML Model flagged behavior as 'high_anomaly'")
    print_step(3, "Agentic AI Investigation...")
    print("  -> LangGraph spawned investigation. Queried OpenSearch RAG.")
    print("  -> Conclusion: Suspicious lateral movement patterns detected, marked as 'potential_zero_day_behavior'")
    print("  -> Risk Score updated to 92/100")

def run_scenario_progression():
    print_step(1, "Analyzing Incident Graph...")
    print("  -> Edges detected: T1190 -> T1059")
    print_step(2, "Predicting Next Attack Phase...")
    print("  -> Top 1 Prediction: T1078 (Valid Accounts)")
    print("  -> Top 2 Prediction: T1569 (System Services)")
    print("  -> Predictions stored separate from observed evidence.")

def run_scenario_response():
    print_step(1, "Checking Recommendations for Incident...")
    print("  -> Recommendation: Block IP 198.51.100.24 (pb_002_block_ip.yml)")
    print_step(2, "Dry Run Execution...")
    print("  -> Simulation passed. Target: 198.51.100.24")
    print_step(3, "Human Approval...")
    print("  -> Requesting manager approval...")
    print("  -> Approval GRANTED by autosoc_admin")
    print_step(4, "Containment Execution...")
    print("  -> Executing via Policy Engine in 'analyst_approved_execution' mode.")
    print("  -> Action Succeeded! IP Blocked.")

def main():
    parser = argparse.ArgumentParser(description="AutoSOC Demo Orchestrator")
    parser.add_argument("--scenario", choices=["benign", "known_threat", "zero_day", "progression", "response", "full_e2e"], 
                        default="full_e2e", help="Scenario to execute")
    
    args = parser.parse_args()
    
    print(f"=== AutoSOC Demo Orchestrator: Starting Scenario '{args.scenario}' ===")
    
    if args.scenario == "benign":
        run_scenario_benign()
    elif args.scenario == "known_threat":
        run_scenario_known_threat()
    elif args.scenario == "zero_day":
        run_scenario_zero_day()
    elif args.scenario == "progression":
        run_scenario_progression()
    elif args.scenario == "response":
        run_scenario_response()
    elif args.scenario == "full_e2e":
        run_scenario_benign()
        time.sleep(2)
        run_scenario_known_threat()
        time.sleep(2)
        run_scenario_zero_day()
        time.sleep(2)
        run_scenario_progression()
        time.sleep(2)
        run_scenario_response()
        
    print("\n=== Demo Complete ===")

if __name__ == "__main__":
    main()
