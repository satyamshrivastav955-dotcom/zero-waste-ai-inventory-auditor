import urllib.request
import json
import os

LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')

def log_debug(msg):
    os.makedirs(LOGS_DIR, exist_ok=True)
    with open(os.path.join(LOGS_DIR, 'debug.log'), 'a') as f:
        f.write(f"[API] {msg}\n")
    print(msg)

def test_endpoint(name, url, method='GET', payload=None):
    try:
        req = urllib.request.Request(url, method=method)
        if payload:
            req.add_header('Content-Type', 'application/json')
            data = json.dumps(payload).encode('utf-8')
            res = urllib.request.urlopen(req, data=data, timeout=5)
        else:
            res = urllib.request.urlopen(req, timeout=5)
            
        status = res.getcode()
        body = res.read().decode('utf-8')
        
        if status == 200:
            log_debug(f"{name} [{method} {url}] -> [PASS]")
            return True
        else:
            log_debug(f"{name} [{method} {url}] -> Status {status} [FAIL]")
            return False
    except Exception as e:
        log_debug(f"{name} [{method} {url}] -> Error: {e} [FAIL]")
        return False

if __name__ == "__main__":
    log_debug("--- Starting API Tests (Requires main.py running) ---")
    base = "http://localhost:5000"
    
    t1 = test_endpoint("Products Fetch", f"{base}/products")
    t2 = test_endpoint("Sensors Fetch", f"{base}/sensors")
    t3 = test_endpoint("Actions Fetch", f"{base}/actions")
    t4 = test_endpoint("History Fetch", f"{base}/history")
    
    t5 = test_endpoint("Sensor Node POST", f"{base}/sensor_data", method='POST', payload={
        "sensor_id": "esp32_test", "temp": 24.5, "humidity": 55.0
    })
    
    t6 = test_endpoint("Recalculate Post", f"{base}/recalculate", method='POST')
    
    if all([t1, t2, t3, t4, t5, t6]):
        log_debug("--- ALL API TESTS: [PASS] ---")
    else:
        log_debug("--- SOME API TESTS: [FAIL] ---")
