import os
import time
import argparse
import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
import mlflow.pytorch
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed", "v1")

class Autoencoder(nn.Module):
    def __init__(self, input_dim):
        super(Autoencoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 4)
        )
        self.decoder = nn.Sequential(
            nn.Linear(4, 8),
            nn.ReLU(),
            nn.Linear(8, 16),
            nn.ReLU(),
            nn.Linear(16, input_dim)
        )
        
    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

def calculate_metrics(y_true, y_pred, is_anomaly=False):
    # In anomaly detection models (IsolationForest, OCSVM): -1 is anomaly (attack), 1 is normal (benign)
    # Our labels: 1 is attack, 0 is benign
    if is_anomaly:
        # Convert -1 to 1 (attack), 1 to 0 (benign)
        y_pred = np.where(y_pred == -1, 1, 0)
        
    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0)
    }
    
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    if cm.shape == (2, 2):
        tn, fp, fn, tp = cm.ravel()
        metrics["fpr"] = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    else:
        metrics["fpr"] = 0.0
        
    return metrics

def train_and_evaluate(dataset_name):
    print(f"Starting baseline training for {dataset_name}...")
    ds_dir = os.path.join(PROCESSED_DIR, dataset_name)
    
    if not os.path.exists(ds_dir):
        print(f"Skipping {dataset_name}: data not found.")
        return
        
    train_df = pd.read_csv(os.path.join(ds_dir, "train.csv"))
    test_df = pd.read_csv(os.path.join(ds_dir, "test.csv"))
    
    X_train = train_df.drop('label', axis=1).values
    y_train = train_df['label'].values
    
    X_test = test_df.drop('label', axis=1).values
    y_test = test_df['label'].values
    
    mlflow.set_experiment(f"autosoc-baseline-{dataset_name}")
    
    models = {
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
        "RandomForest": RandomForestClassifier(n_estimators=50, random_state=42),
        "IsolationForest": IsolationForest(contamination=0.1, random_state=42),
        "OneClassSVM": OneClassSVM(nu=0.1)
    }
    
    for name, model in models.items():
        with mlflow.start_run(run_name=name):
            start_time = time.time()
            if name in ["IsolationForest", "OneClassSVM"]:
                # Train only on benign for anomaly detection
                X_train_benign = X_train[y_train == 0]
                # If dataset is too small, fallback to full train
                if len(X_train_benign) < 5:
                    X_train_benign = X_train
                model.fit(X_train_benign)
                is_anomaly = True
            else:
                model.fit(X_train, y_train)
                is_anomaly = False
                
            train_time = time.time() - start_time
            
            inf_start = time.time()
            y_pred = model.predict(X_test)
            inf_time = time.time() - inf_start
            
            metrics = calculate_metrics(y_test, y_pred, is_anomaly=is_anomaly)
            
            mlflow.log_param("dataset", dataset_name)
            mlflow.log_param("model_type", name)
            
            mlflow.log_metric("train_time", train_time)
            mlflow.log_metric("inference_time", inf_time)
            mlflow.log_metrics(metrics)
            
            if not is_anomaly:
                mlflow.sklearn.log_model(model, "model")
            
            print(f"[{dataset_name}] {name} - F1: {metrics['f1']:.4f} | FPR: {metrics['fpr']:.4f}")
            
    # Autoencoder Baseline
    with mlflow.start_run(run_name="Autoencoder"):
        start_time = time.time()
        input_dim = X_train.shape[1]
        model = Autoencoder(input_dim)
        
        X_train_benign = X_train[y_train == 0]
        if len(X_train_benign) < 5:
            X_train_benign = X_train
            
        tensor_x = torch.Tensor(X_train_benign)
        dataset = TensorDataset(tensor_x, tensor_x)
        loader = DataLoader(dataset, batch_size=32, shuffle=True)
        
        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=0.01)
        
        # Train for 5 epochs to keep it quick
        for epoch in range(5):
            for batch_x, _ in loader:
                optimizer.zero_grad()
                output = model(batch_x)
                loss = criterion(output, batch_x)
                loss.backward()
                optimizer.step()
                
        train_time = time.time() - start_time
        
        # Inference
        inf_start = time.time()
        model.eval()
        with torch.no_grad():
            test_tensor = torch.Tensor(X_test)
            reconstructed = model(test_tensor)
            mse = torch.mean((test_tensor - reconstructed)**2, dim=1).numpy()
            
        # Threshold: 95th percentile of benign training reconstruction error
        with torch.no_grad():
            train_recon = model(tensor_x)
            train_mse = torch.mean((tensor_x - train_recon)**2, dim=1).numpy()
            threshold = np.percentile(train_mse, 95)
            
        inf_time = time.time() - inf_start
        y_pred = (mse > threshold).astype(int)
        
        metrics = calculate_metrics(y_test, y_pred)
        mlflow.log_param("dataset", dataset_name)
        mlflow.log_param("model_type", "Autoencoder")
        mlflow.log_metric("train_time", train_time)
        mlflow.log_metric("inference_time", inf_time)
        mlflow.log_metrics(metrics)
        mlflow.pytorch.log_model(model, "model", serialization_format="pickle")
        
        print(f"[{dataset_name}] Autoencoder - F1: {metrics['f1']:.4f} | FPR: {metrics['fpr']:.4f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["baseline-suite"], help="Command to run")
    parser.add_argument("--profile", default="quick")
    args = parser.parse_args()
    
    if args.command == "baseline-suite":
        # Ensure mlflow runs locally
        os.environ["MLFLOW_ALLOW_FILE_STORE"] = "true"
        os.environ["MLFLOW_TRACKING_URI"] = "sqlite:///mlruns.db"
        for ds in ["unsw_nb15", "cicids2017", "cic_iot_2023"]:
            train_and_evaluate(ds)
