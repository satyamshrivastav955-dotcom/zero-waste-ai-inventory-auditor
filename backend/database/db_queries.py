import sqlite3
import os
import sys

# Ensure config path parses properly when imported top level
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_all_products():
    conn = get_connection()
    res = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return [dict(r) for r in res]

def get_product(sku):
    conn = get_connection()
    res = conn.execute("SELECT * FROM products WHERE sku=?", (sku,)).fetchone()
    conn.close()
    return dict(res) if res else None

def insert_product(sku, name, expiry_date, intake_date, category="General"):
    conn = get_connection()
    res = conn.execute(
        "INSERT INTO products (sku, name, expiry_date, intake_date, category) VALUES (?, ?, ?, ?, ?)",
        (sku, name, expiry_date, intake_date, category)
    )
    product_id = res.lastrowid
    conn.commit()
    conn.close()
    return product_id

def insert_sensor_reading(timestamp, sensor_id, temp, humidity, weight_kg):
    conn = get_connection()
    conn.execute(
        "INSERT INTO sensor_readings (timestamp, sensor_id, temp, humidity, weight_kg) VALUES (?, ?, ?, ?, ?)",
        (timestamp, sensor_id, temp, humidity, weight_kg)
    )
    conn.commit()
    conn.close()

def get_recent_sensor_readings(sensor_id, limit=24):
    conn = get_connection()
    res = conn.execute(
        "SELECT * FROM sensor_readings WHERE sensor_id=? ORDER BY timestamp DESC LIMIT ?", 
        (sensor_id, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in res]

def get_temperature_history(hours=72):
    conn = get_connection()
    # Simple trick in sqlite if timestamp is ISO format
    res = conn.execute(
        "SELECT * FROM sensor_readings WHERE timestamp >= datetime('now', '-' || ? || ' hours') ORDER BY timestamp ASC",
        (hours,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in res]

def insert_weight_history(product_id, timestamp, weight_kg):
    conn = get_connection()
    conn.execute(
        "INSERT INTO weight_history (product_id, timestamp, weight_kg) VALUES (?, ?, ?)",
        (product_id, timestamp, weight_kg)
    )
    conn.commit()
    conn.close()

def get_weight_history(product_id, limit=24):
    conn = get_connection()
    res = conn.execute(
        "SELECT * FROM weight_history WHERE product_id=? ORDER BY timestamp DESC LIMIT ?",
        (product_id, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in res]

def insert_wps_result(product_id, timestamp, ml_prob, expiry_factor, temp_risk, stagnation_penalty, final_wps, status):
    conn = get_connection()
    conn.execute(
        "INSERT INTO wps_results (product_id, timestamp, ml_prob, expiry_factor, temp_risk, stagnation_penalty, final_wps, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (product_id, timestamp, ml_prob, expiry_factor, temp_risk, stagnation_penalty, final_wps, status)
    )
    conn.commit()
    conn.close()

def get_latest_wps(product_id):
    conn = get_connection()
    res = conn.execute("SELECT * FROM wps_results WHERE product_id=? ORDER BY timestamp DESC LIMIT 1", (product_id,)).fetchone()
    conn.close()
    return dict(res) if res else None

def insert_action(product_id, timestamp, wps, action_type, notes):
    conn = get_connection()
    conn.execute(
        "INSERT INTO actions (product_id, timestamp, wps, action_type, notes) VALUES (?, ?, ?, ?, ?)",
        (product_id, timestamp, wps, action_type, notes)
    )
    conn.commit()
    conn.close()

def get_actions(limit=100):
    conn = get_connection()
    query = '''
    SELECT a.*, p.name 
    FROM actions a 
    JOIN products p ON a.product_id = p.id 
    ORDER BY a.timestamp DESC 
    LIMIT ?
    '''
    res = conn.execute(query, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in res]
