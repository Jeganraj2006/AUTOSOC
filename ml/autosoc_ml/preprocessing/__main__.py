import argparse
import os
import pandas as pd
from .adapters import UNSWNB15Adapter, CICIDS2017Adapter, CICIOT2023Adapter
from .pipeline import PreprocessingPipeline

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "raw")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed", "v1")

def get_adapter(dataset_name):
    if dataset_name == "unsw_nb15": return UNSWNB15Adapter()
    if dataset_name == "cicids2017": return CICIDS2017Adapter()
    if dataset_name == "cic_iot_2023": return CICIOT2023Adapter()
    raise ValueError("Unknown dataset")

def get_filename(dataset_name):
    if dataset_name == "unsw_nb15": return "UNSW_NB15_testing-set.csv"
    if dataset_name == "cicids2017": return "CICIDS2017_subset.csv"
    if dataset_name == "cic_iot_2023": return "CIC_IoT2023_subset.csv"
    return ""

def process(dataset_name):
    print(f"Preparing {dataset_name}...")
    file_path = os.path.join(RAW_DIR, dataset_name, get_filename(dataset_name))
    if not os.path.exists(file_path):
        print(f"File missing: {file_path}")
        return
        
    df_raw = pd.read_csv(file_path)
    adapter = get_adapter(dataset_name)
    df_adapted = adapter.adapt(df_raw)
    
    pipeline = PreprocessingPipeline(seed=42)
    dest = os.path.join(PROCESSED_DIR, dataset_name)
    pipeline.prepare_dataset(df_adapted, dest, dataset_name)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["prepare"], help="Command to run")
    parser.add_argument("--dataset", required=True)
    args = parser.parse_args()
    
    if args.command == "prepare":
        if args.dataset == "all":
            for ds in ["unsw_nb15", "cicids2017", "cic_iot_2023"]:
                process(ds)
        else:
            process(args.dataset)
