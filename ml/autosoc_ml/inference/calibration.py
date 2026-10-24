import numpy as np
from sklearn.linear_model import LogisticRegression

class PlattCalibrator:
    """
    Platt Scaling implementation to calibrate supervised model outputs.
    Expects uncalibrated probabilities or logits from the neural network and true labels.
    """
    def __init__(self):
        self.calibrator = LogisticRegression(solver='lbfgs')
        self.is_fitted = False
        
    def fit(self, uncalibrated_preds: np.ndarray, y_true: np.ndarray):
        """
        Fit the Platt scaling function.
        uncalibrated_preds: array of shape (N,)
        y_true: array of shape (N,)
        """
        # Scikit-learn expects 2D array
        X = uncalibrated_preds.reshape(-1, 1)
        self.calibrator.fit(X, y_true)
        self.is_fitted = True
        
    def transform(self, uncalibrated_preds: np.ndarray) -> np.ndarray:
        """
        Return calibrated probabilities.
        """
        if not self.is_fitted:
            raise RuntimeError("Calibrator is not fitted.")
            
        X = uncalibrated_preds.reshape(-1, 1)
        # return probability of class 1
        return self.calibrator.predict_proba(X)[:, 1]
