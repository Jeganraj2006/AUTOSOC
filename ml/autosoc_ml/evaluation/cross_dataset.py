import os
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_score, recall_score
import mlflow

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed", "v1")

def evaluate_cross_dataset():
    print("Cross-Dataset Evaluation")
    os.environ["MLFLOW_ALLOW_FILE_STORE"] = "true"
    os.environ["MLFLOW_TRACKING_URI"] = "file://" + os.path.join(os.path.dirname(PROCESSED_DIR), "..", "..", "mlruns")
    mlflow.set_experiment("autosoc-cross-dataset")
    
    # Train on UNSW-NB15
    train_ds = "unsw_nb15"
    test_ds = "cicids2017"
    
    if not os.path.exists(os.path.join(PROCESSED_DIR, train_ds)):
        print(f"Skipping: {train_ds} not found.")
        return
        
    train_df = pd.read_csv(os.path.join(PROCESSED_DIR, train_ds, "train.csv"))
    X_train = train_df.drop('label', axis=1).values
    y_train = train_df['label'].values
    
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train, y_train)
    
    with mlflow.start_run(run_name=f"train_{train_ds}_test_{test_ds}"):
        test_df = pd.read_csv(os.path.join(PROCESSED_DIR, test_ds, "test.csv"))
        X_test = test_df.drop('label', axis=1).values
        y_test = test_df['label'].values
        
        y_pred = model.predict(X_test)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        
        mlflow.log_param("train_dataset", train_ds)
        mlflow.log_param("test_dataset", test_ds)
        mlflow.log_metric("f1", f1)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        
        print(f"Train: {train_ds} | Test: {test_ds}")
        print(f"F1: {f1:.4f} | Precision: {precision:.4f} | Recall: {recall:.4f}")
        print("Note: Performance might be low due to dataset shift and subset generation artifacts.")

if __name__ == "__main__":
    evaluate_cross_dataset()
