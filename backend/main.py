import os
import sys
import threading
import time
import random
from datetime import datetime, timedelta
from flask import Flask
from flask_cors import CORS

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from config import SIMULATION_MODE, SENSOR_READ_INTERVAL_HOURS, LOGS_DIR
from database.db_init import init_db
from database.db_queries import *
from sensors.sensor_manager import SensorManager
from sensors.barcode_reader import BarcodeScanner
from ml_model.inference import predict
from ml_model.anomaly_detector import analyze_velocity
from wps.temp_risk import calculate_temperature_risk, get_mean_temp_and_humidity
from wps.wps_calculator import calculate_wps
from api.routes import api_bp

app = Flask(__name__)
CORS(app)
app.register_blueprint(api_bp)

sensor_manager = SensorManager()

def simulate_initial_data():
    """Populates enough simulated history for all charts to render on first load (at least 24 data points)"""
    print("[Simulation] Populating fake products and history...")
    products = []
    base_ts = datetime.now() - timedelta(hours=24 * 6) # 6 days ago
    
    # 10 fake products
    for i in range(10):
        expiry = (datetime.now() + timedelta(days=random.randint(7, 180))).strftime('%Y-%m-%d')
        intake = base_ts.isoformat()
        pid = insert_product(f"SIM-SKU-{100+i}", f"Medicine {100+i}", expiry, intake)
        products.append(pid)

    # Fake history 24 points (last 6 days max, interval 6 hours)
    for i in range(24):
        ts = (datetime.now() - timedelta(hours=6*(24-i))).isoformat()
        
        t1, h1 = round(random.uniform(22, 28), 1), round(random.uniform(40, 60), 1)
        insert_sensor_reading(ts, 'pi_node_dht1', t1, h1, None)
        
        t2, h2 = round(random.uniform(22, 28), 1), round(random.uniform(40, 60), 1)
        insert_sensor_reading(ts, 'esp32_1', t2, h2, None)
        
        weight = 5.0 - (i * random.uniform(0.01, 0.05))
        insert_sensor_reading(ts, 'pi_node_scale', None, None, weight)
        
        for pid in products:
            insert_weight_history(pid, ts, weight)
    print("\n[Simulation] Data populated.")

def run_evaluation_cycle():
    print(f"\n[{datetime.now().isoformat()}] --- Starting Routine Evaluation Cycle ---")
    # 1. Read Sensors
    t, h, weight = sensor_manager.perform_routine_read('pi_node')
    
    # 2. Iterate Products and Calculate WPS
    products = get_all_products()
    for p in products:
        pid = p['id']
        name = p['name']
        intake = datetime.fromisoformat(p['intake_date'])
        
        time_in_store = (datetime.now() - intake).days
        
        expiry = datetime.strptime(p['expiry_date'], '%Y-%m-%d')
        days_to_expiry = (expiry - datetime.now()).days
        
        # 3. Features: Velocity & Anomaly
        w_hist = get_weight_history(pid, limit=168) # get a lot of points to allow 7-day EMA
        w_hist.reverse() # chronological
        sm_vel, stag_hrs, anomaly = analyze_velocity(w_hist)
        
        # 4. Features: Temperature Risk
        t_hist_raw = get_temperature_history(hours=72)
        # Assuming product is at pi_node location or we take the worst one
        t_hist = [row for row in t_hist_raw if row['sensor_id'] == 'pi_node_dht1']
        
        t_mean, h_mean, t_exc = get_mean_temp_and_humidity(t_hist)
        temp_risk_index = calculate_temperature_risk(t_hist)
        
        # 5. ML Predict
        features = {
            'days_to_expiry': max(0, days_to_expiry),
            'smoothed_sales_velocity': sm_vel,
            'stock_stagnation_score': stag_hrs / 168.0,
            'temp_mean_72h': t_mean,
            'temp_excursions_72h': t_exc,
            'humidity_mean_72h': h_mean,
            'time_in_store': time_in_store
        }
        
        try:
            ml_prob = predict(features)
        except Exception as e:
            print(f"ML Predict failed ({e}), defaulting to heuristic...")
            ml_prob = 0.5
            
        # 6. Final WPS Calculation & Hardware trigger
        res = calculate_wps(days_to_expiry, ml_prob, temp_risk_index, stag_hrs, pid, name)
        
    print(f"--- Cycle Complete ---\n")

def background_scheduler():
    while True:
        # Sleep until next interval
        time.sleep(SENSOR_READ_INTERVAL_HOURS * 3600)
        run_evaluation_cycle()

def on_barcode_scanned(code):
    print(f"\n[Barcode Scanned]: {code}")
    # Provide simple logic to add product
    from config import DB_PATH
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id FROM products WHERE sku=?", (code,))
    if cur.fetchone() is None:
        expiry = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
        insert_product(code, f"Scanned Item {code[-4:]}", expiry, datetime.now().isoformat())
        print(f"-> Added new product {code}")
    else:
        print(f"-> Product {code} already exists.")
    conn.close()

if __name__ == '__main__':
    print("====================================")
    print(" Zero-Waste AI Inventory Auditor")
    print("====================================")
    print(f"SIMULATION_MODE = {SIMULATION_MODE}")

    # Initialize DB
    init_db()
    
    # Train ML if not exists
    from config import MODEL_PATH
    if not os.path.exists(MODEL_PATH):
        print("ML model not found. Training now...")
        from ml_model.train_model import train_and_save
        train_and_save()

    if SIMULATION_MODE:
        prods = get_all_products()
        if not prods:
            simulate_initial_data()

    # Start Barcode Scanner Background
    scanner = BarcodeScanner(on_barcode_scanned)
    scanner.start()
    
    # Start Scheduler
    t = threading.Thread(target=background_scheduler, daemon=True)
    t.start()
    
    # Initial Evaluation
    if not get_all_products() == []:
        run_evaluation_cycle()

    # Avoid port collision / reloader issues with flask and threading
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
