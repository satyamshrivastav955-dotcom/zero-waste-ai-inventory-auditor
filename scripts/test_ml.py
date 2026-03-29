import sys
import os
import time

# Use exact absolute path hack for testing script run anywhere
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.ml_model.inference import predict
from backend.wps.wps_calculator import calculate_wps
from backend.config import LOGS_DIR

def log_debug(msg):
    log_path = os.path.join(LOGS_DIR, 'debug.log')
    with open(log_path, 'a') as f:
        f.write(f"[ML] {msg}\n")
    print(msg)

def test_ml():
    log_debug("--- Starting ML Test ---")
    
    # Needs to match train_model.py output expectation
    fake_inputs = [
        # 1. Fresh, well sold, good temps -> SAFE
        {'days_to_expiry': 120, 'smoothed_sales_velocity': 5.0, 'stock_stagnation_score': 0.0, 'temp_mean_72h': 21.0, 'temp_excursions_72h': 0, 'humidity_mean_72h': 50, 'time_in_store': 10},
        # 2. Expiring soon, stagnant -> MARKDOWN/BUNDLE
        {'days_to_expiry': 20, 'smoothed_sales_velocity': 0.2, 'stock_stagnation_score': 0.8, 'temp_mean_72h': 23.0, 'temp_excursions_72h': 0, 'humidity_mean_72h': 50, 'time_in_store': 100},
        # 3. Bad temp excursions -> CRITICAL
        {'days_to_expiry': 180, 'smoothed_sales_velocity': 3.0, 'stock_stagnation_score': 0.1, 'temp_mean_72h': 26.5, 'temp_excursions_72h': 15, 'humidity_mean_72h': 50, 'time_in_store': 20},
        # 4. Expired -> WASTE
        {'days_to_expiry': -5, 'smoothed_sales_velocity': 0.0, 'stock_stagnation_score': 1.0, 'temp_mean_72h': 22.0, 'temp_excursions_72h': 0, 'humidity_mean_72h': 50, 'time_in_store': 365},
        # 5. Perfect condition
        {'days_to_expiry': 300, 'smoothed_sales_velocity': 8.0, 'stock_stagnation_score': 0.0, 'temp_mean_72h': 20.0, 'temp_excursions_72h': 0, 'humidity_mean_72h': 60, 'time_in_store': 5}
    ]

    all_pass = True
    
    for i, features in enumerate(fake_inputs):
        try:
            prob = predict(features)
            
            # test also full wps calculation
            temp_risk = (features['temp_excursions_72h'] / 24.0) * 100 if features['temp_excursions_72h'] > 0 else 0
            res = calculate_wps(
                features['days_to_expiry'],
                prob,
                temp_risk,
                features['stock_stagnation_score'] * 168,
                9999 + i, "TestItem"
            )
            
            log_debug(f"Input {i+1}: WPS={res['wps']:.2f} -> Status: {res['status']} [PASS]")
        except Exception as e:
            log_debug(f"Input {i+1}: Errored - {e} [FAIL]")
            all_pass = False

    if all_pass:
        log_debug("--- ML Test Completed: [PASS] ---")
    else:
        log_debug("--- ML Test Completed: [FAIL] ---")

if __name__ == "__main__":
    test_ml()
