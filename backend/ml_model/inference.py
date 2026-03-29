import pickle
import os
import sys
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MODEL_PATH

class WPSInference:
    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found at {MODEL_PATH}. Run train_model.py first.")
        with open(MODEL_PATH, 'rb') as f:
            self.model = pickle.load(f)

    def predict_prob(self, features_dict):
        """
        Features expected:
        days_to_expiry, smoothed_sales_velocity, stock_stagnation_score,
        temp_mean_72h, temp_excursions_72h, humidity_mean_72h, time_in_store
        """
        if self.model is None:
            self._load_model()

        # Build dataframe in same order as training
        df = pd.DataFrame([features_dict])
        
        # Output probability for class 1 (waste)
        probs = self.model.predict_proba(df)
        if probs.shape[1] > 1:
            return float(probs[0, 1])
        else:
            # edge case if only 1 class in training
            return float(probs[0, 0])

# Singleton-like instance for ease of use
_inference_instance = None

def predict(features_dict):
    global _inference_instance
    if _inference_instance is None:
        _inference_instance = WPSInference()
    return _inference_instance.predict_prob(features_dict)
