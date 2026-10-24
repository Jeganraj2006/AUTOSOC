import os
import pandas as pd
import mlflow
from mlflow.tracking import MlflowClient

def get_dir_size(path):
    total_size = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size / (1024 * 1024)

def run():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "ml", "autosoc_ml", "datasets"))
    raw_dir = os.path.join(base_dir, "raw")
    proc_dir = os.path.join(base_dir, "processed", "v1")
    
    print("=== DATASET STATISTICS ===")
    
    for ds in ["unsw_nb15", "cicids2017", "cic_iot_2023"]:
        print(f"\n[{ds.upper()}]")
        raw_size = get_dir_size(os.path.join(raw_dir, ds))
        proc_size = get_dir_size(os.path.join(proc_dir, ds))
        print(f"  Raw Directory Size: {raw_size:.2f} MB")
        print(f"  Processed Directory Size: {proc_size:.2f} MB")
        
        try:
            train_df = pd.read_csv(os.path.join(proc_dir, ds, "train.csv"))
            val_df = pd.read_csv(os.path.join(proc_dir, ds, "val.csv"))
            test_df = pd.read_csv(os.path.join(proc_dir, ds, "test.csv"))
            print(f"  Processed Splits -> Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")
        except Exception as e:
            print("  Could not read splits:", e)
            
    print("\n=== MLFLOW MODEL METRICS & RUN IDs ===")
    os.environ["MLFLOW_TRACKING_URI"] = "sqlite:///mlruns.db"
    client = MlflowClient()
    
    experiments = client.search_experiments()
    for exp in experiments:
        if not exp.name.startswith("autosoc-baseline"):
            continue
        print(f"\nExperiment: {exp.name}")
        runs = client.search_runs(experiment_ids=[exp.experiment_id])
        for run in runs:
            run_id = run.info.run_id
            run_name = run.data.tags.get("mlflow.runName", "unknown")
            f1 = run.data.metrics.get("f1", "N/A")
            fpr = run.data.metrics.get("fpr", "N/A")
            print(f"  Run ID: {run_id} | Model: {run_name} | F1: {f1} | FPR: {fpr}")

if __name__ == "__main__":
    run()
