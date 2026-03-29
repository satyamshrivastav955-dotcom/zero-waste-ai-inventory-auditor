import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.sensors.load_cell_reader import LoadCellReader
from backend.config import LOGS_DIR

def log_debug(msg):
    os.makedirs(LOGS_DIR, exist_ok=True)
    with open(os.path.join(LOGS_DIR, 'debug.log'), 'a') as f:
        f.write(f"[LOAD_CELL] {msg}\n")
    print(msg)

def run_test():
    log_debug("--- Starting Load Cell Test ---")
    
    lc = LoadCellReader()
    passes = 0
    fails = 0
    
    # Read every 1s
    for i in range(15):
        try:
            val = lc.read_weight_kg()
            if val is not None:
                log_debug(f"Read {i+1}: raw/calibrated weight = {val} kg -> [PASS]")
                passes += 1
            else:
                log_debug(f"Read {i+1}: returned None -> [FAIL]")
                fails += 1
        except Exception as e:
            log_debug(f"Read {i+1}: Error: {e} -> [FAIL]")
            fails += 1
        time.sleep(1.0)
    
    if passes > 0:
        log_debug("[OVERALL HX711 PASS]")
    else:
        log_debug("[OVERALL HX711 FAIL]")

if __name__ == "__main__":
    run_test()
