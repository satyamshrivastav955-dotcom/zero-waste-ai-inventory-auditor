import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sensors.dht22_reader import DHT22Reader
from sensors.load_cell_reader import LoadCellReader
from database.db_queries import insert_sensor_reading, insert_weight_history, get_all_products

class SensorManager:
    def __init__(self):
        self.dht = DHT22Reader()
        self.load_cell = LoadCellReader()

    def perform_routine_read(self, sensor_id_prefix="dht22_local"):
        t, h = self.dht.read()
        ts = datetime.now().isoformat()
        
        weight = self.load_cell.read_weight_kg()

        # Save general temperature/humidity
        if t is not None and h is not None:
            insert_sensor_reading(ts, sensor_id_prefix, t, h, None)

        # Assuming load cell represents the collective stack or global velocity proxy
        insert_sensor_reading(ts, "load_cell_main", None, None, weight)
        
        # Link weight to all active products for temporal ML analytics
        products = get_all_products()
        for p in products:
            insert_weight_history(p['id'], ts, weight)
            
        print(f"[{ts}] Sensor read complete: Temp={t}C, Hum={h}%, Weight={weight}kg")
        return t, h, weight
