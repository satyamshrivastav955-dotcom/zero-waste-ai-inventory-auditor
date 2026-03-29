import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import pickle
import os
import sys

# Ensure config path parses properly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MODEL_PATH

def generate_synthetic_data(n_samples=500):
    np.random.seed(42)  # For reproducibility

    # 1. Generate features based on requested distributions
    days_to_expiry = np.random.uniform(1, 365, n_samples)
    
    # Exponential for sales velocity, slower near expiry (simulating real behavior)
    smoothed_sales_velocity = np.random.exponential(scale=1.0, size=n_samples)
    mask_near_expiry = days_to_expiry < 30
    smoothed_sales_velocity[mask_near_expiry] *= 0.2

    temp_mean_72h = np.random.normal(25, 3, n_samples)
    temp_excursions_72h = np.random.poisson(2, n_samples)
    stock_stagnation_score = np.random.uniform(0, 1, n_samples)
    time_in_store = np.random.uniform(1, 90, n_samples)
    humidity_mean_72h = np.random.normal(55, 10, n_samples)

    data = pd.DataFrame({
        'days_to_expiry': days_to_expiry,
        'smoothed_sales_velocity': smoothed_sales_velocity,
        'stock_stagnation_score': stock_stagnation_score,
        'temp_mean_72h': temp_mean_72h,
        'temp_excursions_72h': temp_excursions_72h,
        'humidity_mean_72h': humidity_mean_72h,
        'time_in_store': time_in_store
    })

    # 2. Label generation (weak supervision)
    # waste = 1 if (days_to_expiry < 14 AND velocity < 0.1) OR (stagnation_score > 0.7 AND days_to_expiry < 30)
    cond1 = (data['days_to_expiry'] < 14) & (data['smoothed_sales_velocity'] < 0.1)
    cond2 = (data['stock_stagnation_score'] > 0.7) & (data['days_to_expiry'] < 30)
    
    data['waste_label'] = np.where(cond1 | cond2, 1, 0)

    # Some noise for reality
    noise_indices = np.random.choice(n_samples, size=int(0.05 * n_samples), replace=False)
    data.loc[noise_indices, 'waste_label'] = 1 - data.loc[noise_indices, 'waste_label']

    return data

def train_and_save():
    print("Generating synthetic data...")
    df = generate_synthetic_data()

    X = df.drop(columns=['waste_label'])
    y = df['waste_label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print("Training Random Forest Classifier (max_trees=50, max_depth=5)...")
    clf = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    print("\n--- Model Evaluation ---")
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1 Score:  {f1:.4f}")

    print("\n--- Feature Importances ---")
    importances = clf.feature_importances_
    features = X.columns
    for f, imp in sorted(zip(features, importances), key=lambda x: x[1], reverse=True):
        print(f"{f}: {imp:.4f}")

    # Save to disk
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(clf, f)
    print(f"\nModel saved successfully at: {MODEL_PATH}")

if __name__ == "__main__":
    train_and_save()
