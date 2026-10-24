import pandas as pd
import os
import json

RAW_DIR = os.path.join(os.path.dirname(__file__), "raw")
DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "docs")

def inspect_dataset(dataset_name, filename, doc_id, label_col):
    df = pd.read_csv(os.path.join(RAW_DIR, dataset_name, filename))
    
    num_rows, num_cols = df.shape
    label_counts = df[label_col].value_counts().to_dict()
    missing_values = df.isnull().sum().sum()
    duplicate_rows = df.duplicated().sum()
    
    numeric_cols = df.select_dtypes(include=['number']).columns
    inf_count = 0
    if len(numeric_cols) > 0:
        inf_count = df[numeric_cols].isin([float('inf'), float('-inf')]).sum().sum()
        
    doc_content = f"""# {dataset_name.upper()} Dataset Analysis

## Basic Statistics
- **Rows**: {num_rows}
- **Columns**: {num_cols}
- **Missing Values**: {missing_values}
- **Duplicate Rows**: {duplicate_rows}
- **Infinity Values**: {inf_count}

## Label Distribution
```json
{json.dumps(label_counts, indent=2)}
```

## Schema
```
{', '.join(df.columns.tolist())}
```
"""
    with open(os.path.join(DOCS_DIR, f"{doc_id}-{dataset_name.replace('_', '-')}-analysis.md"), "w") as f:
        f.write(doc_content)
    print(f"Generated {doc_id} for {dataset_name}")

if __name__ == "__main__":
    inspect_dataset("unsw_nb15", "UNSW_NB15_testing-set.csv", "121", "label")
    inspect_dataset("cicids2017", "CICIDS2017_subset.csv", "122", "Label")
    inspect_dataset("cic_iot_2023", "CIC_IoT2023_subset.csv", "123", "label")
