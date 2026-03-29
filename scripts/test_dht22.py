import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.sensors.dht22_reader import DHT22Reader
from backend.config import LOGS_DIR

def log_debug(msg):
    os.makedirs(LOGS_DIR, exist_ok=True)
    with open(os.path.join(LOGS_DIR, 'debug.log'), 'a') as f:
        f.write(f"[DHT] {msg}\n")
    print(msg)

def run_test():
    log_debug("--- Starting DHT22 Test ---")
    dht = DHT22Reader()
    
    passes = 0
    fails = 0
    
    # Read every 2s for 30s
    for i in range(15):
        t, h = dht.read()
        if t is not None and h is not None:
            log_debug(f"Read {i+1}: {t}C / {h}% -> [PASS]")
            passes += 1
        else:
            log_debug(f"Read {i+1}: Sensor returned None -> [FAIL]")
            fails += 1
        time.sleep(2.0)
        
    log_debug(f"--- DHT22 Test Completed: Passes {passes}, Fails {fails} ---")
    if passes > 0:
        log_debug("[OVERALL DHT PASS]")
    else:
        log_debug("[OVERALL DHT FAIL]")

if __name__ == "__main__":
    run_test()
