import sys
import os
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SIMULATION_MODE, PIN_HX711_DOUT, PIN_HX711_SCK

if not SIMULATION_MODE:
    try:
        # User needs to pip install hx711
        from hx711 import HX711 
    except ImportError:
        pass

class LoadCellReader:
    def __init__(self):
        self.sim_weight = 5.0
        self.hx = None
        if not SIMULATION_MODE and 'HX711' in sys.modules:
            try:
                self.hx = HX711(dout_pin=PIN_HX711_DOUT, pd_sck_pin=PIN_HX711_SCK)
                # Hardcoded calibration ratio for initial setup. Real value via test script
                self.hx.set_scale_ratio(100.0) 
                self.hx.reset()
            except Exception as e:
                print(f"HX711 Setup Error: {e}")

    def read_weight_kg(self):
        if SIMULATION_MODE:
            drop = random.uniform(0.01, 0.1)
            # 5% chance of stagnation
            if random.random() < 0.05:
                drop = 0.0
            self.sim_weight = max(0.0, self.sim_weight - drop)
            return round(self.sim_weight, 3)
        
        if self.hx:
            try:
                raw_grams = self.hx.get_weight_mean(readings=3)
                if raw_grams is not None:
                    return round(raw_grams / 1000.0, 3)
            except Exception:
                return 0.0
        return 0.0
