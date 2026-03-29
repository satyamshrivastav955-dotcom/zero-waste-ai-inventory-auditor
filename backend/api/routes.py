import sys
import os
from flask import Blueprint, jsonify, request, send_from_directory
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_queries import *

api_bp = Blueprint('api', __name__)

# Serve Frontend
@api_bp.route('/')
def serve_index():
    return send_from_directory(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '../frontend'), 'index.html')

@api_bp.route('/<path:path>')
def serve_static(path):
    return send_from_directory(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '../frontend'), path)


@api_bp.route('/products', methods=['GET'])
def get_products_data():
    products = get_all_products()
    for p in products:
        wps_data = get_latest_wps(p['id'])
        if wps_data:
            p.update(wps_data)
        else:
            p['status'] = "Pending"
            p['final_wps'] = 0.0
            
        # Calc time in store
        intake = datetime.fromisoformat(p['intake_date'])
        p['time_in_store_days'] = (datetime.now() - intake).days
        
        # Calc days to expiry
        expiry = datetime.strptime(p['expiry_date'], '%Y-%m-%d')
        p['days_to_expiry'] = (expiry - datetime.now()).days

    return jsonify({"products": products})

@api_bp.route('/sensors', methods=['GET'])
def get_sensors_data():
    dht_local = get_recent_sensor_readings('pi_node_dht1', limit=1)
    dht_esp = get_recent_sensor_readings('esp32_1', limit=1)
    scale = get_recent_sensor_readings('pi_node_scale', limit=1)
    
    return jsonify({
        "dht_local": dht_local[0] if dht_local else None,
        "dht_node": dht_esp[0] if dht_esp else None,
        "load_cell": scale[0] if scale else None
    })

@api_bp.route('/actions', methods=['GET'])
def get_actions_api():
    logs = get_actions(limit=50)
    return jsonify({"actions": logs})

@api_bp.route('/history', methods=['GET'])
def get_history_api():
    temp_hist = get_temperature_history(hours=24) # Fetch 24 hours of data
    
    # Structure for Chart.js
    # We want to separate local vs node
    local_t = []
    esp_t = []
    labels = set()
    
    for r in temp_hist:
        ts = r['timestamp']
        labels.add(ts)
        if r['sensor_id'] == 'pi_node_dht1':
            local_t.append({"x": ts, "y": r['temp']})
        elif r['sensor_id'] == 'esp32_1':
            esp_t.append({"x": ts, "y": r['temp']})

    # Find the top active product to show weight history
    products = get_all_products()
    weight_hist = []
    if products:
        # Just use the first product's history since we simulate a single scale proxy
        raw_w = get_weight_history(products[0]['id'], limit=24)
        for w in raw_w:
            weight_hist.append({"x": w['timestamp'], "y": w['weight_kg']})

    return jsonify({
        "temperature": {
            "local": local_t,
            "node": esp_t
        },
        "weight": weight_hist
    })

@api_bp.route('/sensor_data', methods=['POST'])
def post_sensor_data():
    """ESP32 Node posts data here."""
    data = request.json
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    
    sensor_id = data.get("sensor_id", "esp32_1")
    temp = data.get("temp")
    humidity = data.get("humidity")
    timestamp = data.get("timestamp") or datetime.now().isoformat()
    
    insert_sensor_reading(timestamp, sensor_id, temp, humidity, None)
    return jsonify({"status": "received", "timestamp": timestamp})

@api_bp.route('/recalculate', methods=['POST'])
def force_recalculate():
    # Will be hooked in main
    from main import run_evaluation_cycle
    run_evaluation_cycle()
    return jsonify({"status": "Evaluation completed"})
