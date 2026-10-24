import os
import time
import argparse
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import mlflow
import mlflow.pytorch
import hashlib

from autosoc_ml.sequence.builder import SequenceBuilder
from autosoc_ml.models.cnn import CnnDetector
from autosoc_ml.models.lstm import LstmDetector
from autosoc_ml.models.transformer import TransformerDetector
from autosoc_ml.models.anomaly import AdvancedAutoencoder
from autosoc_ml.inference.calibration import PlattCalibrator
from autosoc_ml.inference.fusion import fuse_supervised_outputs

# Setup paths
BASE_DIR = os.path.dirname(__file__)
PROCESSED_DIR = os.path.join(BASE_DIR, "..", "datasets", "processed", "v1")
os.environ["MLFLOW_ALLOW_FILE_STORE"] = "true"
os.environ["MLFLOW_TRACKING_URI"] = "sqlite:///mlruns.db"

def calculate_metrics(y_true, y_pred):
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    fpr = cm[0, 1] / (cm[0, 1] + cm[0, 0]) if (cm[0, 1] + cm[0, 0]) > 0 else 0.0
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "fpr": fpr
    }

def generate_hash(filepath):
    if not os.path.exists(filepath):
        return "N/A"
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def train_supervised_model(model, train_loader, val_loader, epochs=5, lr=0.01):
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    model.train()
    start_time = time.time()
    for epoch in range(epochs):
        for batch_x, batch_y in train_loader:
            optimizer.zero_grad()
            output = model(batch_x).squeeze(-1)
            loss = criterion(output, batch_y)
            loss.backward()
            optimizer.step()
    train_time = time.time() - start_time
    
    # Evaluate on val set for calibration
    model.eval()
    val_preds, val_targets = [], []
    with torch.no_grad():
        for batch_x, batch_y in val_loader:
            output = model(batch_x).squeeze(-1)
            val_preds.extend(output.numpy())
            val_targets.extend(batch_y.numpy())
            
    val_preds = np.array(val_preds)
    val_targets = np.array(val_targets)
    
    # Calibration
    calibrator = PlattCalibrator()
    calibrator.fit(val_preds, val_targets)
    
    return model, calibrator, train_time

def train_anomaly_model(model, train_loader, epochs=5, lr=0.01):
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    model.train()
    start_time = time.time()
    for epoch in range(epochs):
        for batch_x, _ in train_loader:
            optimizer.zero_grad()
            # We want to reconstruct the last step of the sequence
            target = batch_x[:, -1, :] 
            output = model(target)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
    return model, time.time() - start_time

def run_hybrid_suite(dataset_name):
    print(f"\n[Hybrid Suite] Starting training for {dataset_name}...")
    ds_dir = os.path.join(PROCESSED_DIR, dataset_name)
    if not os.path.exists(ds_dir):
        print(f"Skipping {dataset_name}: data not found.")
        return
        
    train_df = pd.read_csv(os.path.join(ds_dir, "train.csv"))
    val_df = pd.read_csv(os.path.join(ds_dir, "val.csv"))
    test_df = pd.read_csv(os.path.join(ds_dir, "test.csv"))
    
    builder = SequenceBuilder(max_seq_len=5, feature_dim=7)
    
    X_train = builder.build_from_dataframe(train_df.drop('label', axis=1))
    y_train = train_df['label'].values.astype(np.float32)
    
    X_val = builder.build_from_dataframe(val_df.drop('label', axis=1))
    y_val = val_df['label'].values.astype(np.float32)
    
    X_test = builder.build_from_dataframe(test_df.drop('label', axis=1))
    y_test = test_df['label'].values.astype(np.float32)
    
    train_loader = DataLoader(TensorDataset(torch.Tensor(X_train), torch.Tensor(y_train)), batch_size=32, shuffle=True)
    val_loader = DataLoader(TensorDataset(torch.Tensor(X_val), torch.Tensor(y_val)), batch_size=32, shuffle=False)
    test_loader = DataLoader(TensorDataset(torch.Tensor(X_test), torch.Tensor(y_test)), batch_size=32, shuffle=False)
    
    mlflow.set_experiment(f"autosoc-hybrid-{dataset_name}")
    
    models = {
        "CNN": CnnDetector(feature_dim=7, seq_len=5),
        "LSTM": LstmDetector(feature_dim=7, hidden_size=16),
        "Transformer": TransformerDetector(feature_dim=7, d_model=16, nhead=2)
    }
    
    calibrators = {}
    test_preds = {}
    
    # 1. Train Supervised Models
    for name, model in models.items():
        with mlflow.start_run(run_name=name):
            print(f"Training {name}...")
            model, calibrator, train_time = train_supervised_model(model, train_loader, val_loader)
            calibrators[name] = calibrator
            
            # Inference on Test Set
            inf_start = time.time()
            model.eval()
            raw_preds = []
            with torch.no_grad():
                for batch_x, _ in test_loader:
                    out = model(batch_x).squeeze(-1)
                    raw_preds.extend(out.numpy())
            raw_preds = np.array(raw_preds)
            inf_time = time.time() - inf_start
            
            calib_preds = calibrator.transform(raw_preds)
            test_preds[name] = calib_preds
            
            y_pred_class = (calib_preds > 0.5).astype(int)
            metrics = calculate_metrics(y_test, y_pred_class)
            
            mlflow.log_param("dataset", dataset_name)
            mlflow.log_metric("train_time", train_time)
            mlflow.log_metric("inference_time", inf_time)
            mlflow.log_metrics(metrics)
            mlflow.pytorch.log_model(model, "model", serialization_format="pickle")
            
            print(f"[{dataset_name}] {name} - F1: {metrics['f1']:.4f} | FPR: {metrics['fpr']:.4f}")

    # 2. Train Anomaly Model
    with mlflow.start_run(run_name="AnomalyAutoencoder"):
        print(f"Training AnomalyAutoencoder...")
        anomaly_model = AdvancedAutoencoder(input_dim=7)
        # Train only on benign
        benign_indices = np.where(y_train == 0)[0]
        if len(benign_indices) < 5: benign_indices = np.arange(len(y_train))
        
        X_train_benign = X_train[benign_indices]
        benign_loader = DataLoader(TensorDataset(torch.Tensor(X_train_benign), torch.Tensor(X_train_benign)), batch_size=32, shuffle=True)
        
        anomaly_model, train_time = train_anomaly_model(anomaly_model, benign_loader)
        
        # Inference on Test Set
        inf_start = time.time()
        anomaly_model.eval()
        recon_errors = []
        with torch.no_grad():
            for batch_x, _ in test_loader:
                target = batch_x[:, -1, :]
                recon = anomaly_model(target)
                mse = torch.mean((target - recon)**2, dim=1)
                recon_errors.extend(mse.numpy())
        recon_errors = np.array(recon_errors)
        inf_time = time.time() - inf_start
        
        # Calculate threshold on training benign set
        anomaly_model.eval()
        with torch.no_grad():
            target_benign = torch.Tensor(X_train_benign[:, -1, :])
            recon_benign = anomaly_model(target_benign)
            mse_benign = torch.mean((target_benign - recon_benign)**2, dim=1).numpy()
            threshold = np.percentile(mse_benign, 95)
            # Normalization limits for MinMax scaling [0,1]
            min_val = mse_benign.min()
            max_val = np.percentile(mse_benign, 99.9) # 99.9th percentile to clamp extreme outliers
            if max_val == min_val: max_val = min_val + 1e-5
            
        test_preds["Anomaly"] = np.clip((recon_errors - min_val) / (max_val - min_val), 0, 1)
        
        y_pred_anomaly = (recon_errors > threshold).astype(int)
        metrics = calculate_metrics(y_test, y_pred_anomaly)
        
        mlflow.log_param("dataset", dataset_name)
        mlflow.log_metric("train_time", train_time)
        mlflow.log_metric("inference_time", inf_time)
        mlflow.log_metric("threshold", threshold)
        mlflow.log_metrics(metrics)
        mlflow.pytorch.log_model(anomaly_model, "model", serialization_format="pickle")
        print(f"[{dataset_name}] Anomaly - F1: {metrics['f1']:.4f} | FPR: {metrics['fpr']:.4f}")

    # 3. Hybrid Fusion Ablation & MLflow Logging
    with mlflow.start_run(run_name="HybridFusion"):
        fused_probs = np.array([
            fuse_supervised_outputs(test_preds["CNN"][i], test_preds["LSTM"][i], test_preds["Transformer"][i])
            for i in range(len(y_test))
        ])
        
        y_pred_fused = (fused_probs > 0.5).astype(int)
        hybrid_metrics = calculate_metrics(y_test, y_pred_fused)
        
        mlflow.log_param("dataset", dataset_name)
        mlflow.log_metrics({f"hybrid_{k}": v for k, v in hybrid_metrics.items()})
        print(f"[{dataset_name}] HybridFusion - F1: {hybrid_metrics['f1']:.4f} | FPR: {hybrid_metrics['fpr']:.4f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["quick"])
    args = parser.parse_args()
    
    if args.command == "quick":
        for ds in ["unsw_nb15", "cicids2017", "cic_iot_2023"]:
            run_hybrid_suite(ds)
