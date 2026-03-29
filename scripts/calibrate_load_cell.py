import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import PIN_HX711_DOUT, PIN_HX711_SCK, SIMULATION_MODE

def run_calibration():
    print("--- HX711 Interactive Calibration ---")
    if SIMULATION_MODE:
        print("SIMULATION_MODE is ON. Switch to False in config.py to calibrate real hardware.")
        # provide interactive simulation for test
        print("Empty the scale. Taring...")
        time.sleep(1)
        w = input("Place a known weight (in GRAMS) and enter value: ")
        print(f"Calibration Ratio simulating: 123.45")
        return

    try:
        from hx711 import HX711
        hx = HX711(dout_pin=PIN_HX711_DOUT, pd_sck_pin=PIN_HX711_SCK)
        err = hx.reset()
        if err:
            print("HX711 Init Failure. Setup error.")
            return
            
        print("Empty the scale. Taring in 3 seconds...")
        time.sleep(3)
        hx.tare()
        print("Tare Complete.")
        
        known_weight = input("Place a known weight in GRAMS, enter value: ")
        try:
            known_weight = float(known_weight)
        except ValueError:
            print("Invalid weight entry. Must be number.")
            return
            
        print("Reading...")
        raw_val = hx.get_data_mean(readings=30)
        
        if raw_val:
            ratio = raw_val / known_weight
            print(f"\n[PASS] Calibration Ratio is: {ratio}")
            print("Update load_cell_reader.py: self.hx.set_scale_ratio(ratio) with this number.")
        else:
            print("[FAIL] Failed to get stable reading.")
    except Exception as e:
        print(f"Error during calibration: {e}")

if __name__ == "__main__":
    run_calibration()
