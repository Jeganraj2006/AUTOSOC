import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import os
import joblib

class PreprocessingPipeline:
    def __init__(self, seed=42):
        self.seed = seed
        self.scaler = StandardScaler()
        self.features = ['duration', 'proto_tcp', 'proto_udp', 'fwd_pkts', 'bwd_pkts', 'fwd_bytes', 'bwd_bytes']
        
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df_dedup = df.drop_duplicates()
        if len(df_dedup) < 10:
            print("WARNING: Dataset too small after deduplication. Skipping deduplication to allow stratify.")
        else:
            df = df_dedup
            
        # Handle NA and inf
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.fillna(df.median(numeric_only=True))
        return df

    def prepare_dataset(self, df: pd.DataFrame, dest_dir: str, dataset_name: str, unseen_class=None):
        df_clean = self.clean(df)
        
        # Isolate unseen class if specified for Unseen Attack Evaluation
        unseen_test = None
        if unseen_class:
            # We don't have sub-families mapped in this subset generation to keep it simple, 
            # but structurally this is how it would be isolated.
            pass
            
        X = df_clean[self.features]
        # label mapping string to numeric binary: 0=benign, 1=attack
        y = df_clean['label'].apply(lambda x: 1 if x == 'attack' else 0)
        
        # Stratified Split 70/15/15
        X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=self.seed, stratify=y)
        X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=self.seed, stratify=y_temp)
        
        # Scaling (fit only on train)
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Create output directories
        os.makedirs(dest_dir, exist_ok=True)
        
        # Save splits (X and y concatenated for simplicity, or separate)
        train_out = pd.DataFrame(X_train_scaled, columns=self.features)
        train_out['label'] = y_train.values
        train_out.to_csv(os.path.join(dest_dir, "train.csv"), index=False)
        
        val_out = pd.DataFrame(X_val_scaled, columns=self.features)
        val_out['label'] = y_val.values
        val_out.to_csv(os.path.join(dest_dir, "val.csv"), index=False)
        
        test_out = pd.DataFrame(X_test_scaled, columns=self.features)
        test_out['label'] = y_test.values
        test_out.to_csv(os.path.join(dest_dir, "test.csv"), index=False)
        
        # Save scaler artifact safely
        joblib.dump(self.scaler, os.path.join(dest_dir, "scaler.joblib"))
        
        print(f"[{dataset_name}] Pipeline completed.")
        print(f"  Train: {len(train_out)} | Val: {len(val_out)} | Test: {len(test_out)}")
