import sys
import os
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SIMULATION_MODE, PIN_DHT22_1

if not SIMULATION_MODE:
    try:
        import board
        import adafruit_dht
    except ImportError:
        pass

class DHT22Reader:
    def __init__(self, pin=PIN_DHT22_1):
        self.pin = pin
        self.sensor = None
        if not SIMULATION_MODE:
            if 'board' in sys.modules and 'adafruit_dht' in sys.modules:
                pin_attr = getattr(board, f'D{self.pin}', None)
                if pin_attr:
                    self.sensor = adafruit_dht.DHT22(pin_attr)

    def read(self):
        """Returns (temperature_c, humidity_percent)"""
        if SIMULATION_MODE:
            return round(random.uniform(22.0, 32.0), 1), round(random.uniform(40.0, 80.0), 1)
        
        if self.sensor:
            try:
                t = self.sensor.temperature
                h = self.sensor.humidity
                if t is not None and h is not None:
                    return round(t, 1), round(h, 1)
            except RuntimeError as error:
                # common to fail reading
                pass
        return None, None
