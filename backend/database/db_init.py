import sqlite3
import os
import sys

# Add backend directory to sys.path so config import works natively
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Product Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT UNIQUE,
        name TEXT,
        expiry_date TEXT,
        intake_date TEXT,
        category TEXT
    )
    ''')

    # Sensor Readings
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sensor_readings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        sensor_id TEXT,
        temp REAL,
        humidity REAL,
        weight_kg REAL
    )
    ''')

    # Weight History per product (useful when load cell proxy maps to product)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS weight_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        timestamp TEXT,
        weight_kg REAL,
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    ''')

    # WPS Results Storage
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS wps_results(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        timestamp TEXT,
        ml_prob REAL,
        expiry_factor REAL,
        temp_risk REAL,
        stagnation_penalty REAL,
        final_wps REAL,
        status TEXT,
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    ''')

    # Action logs (markdown, safe, etc)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS actions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        timestamp TEXT,
        wps REAL,
        action_type TEXT,
        notes TEXT,
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    print("Initializing Database Schema...")
    init_db()
    print("Database Initialized successfully.")
