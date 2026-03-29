import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TEMP_THRESHOLD_C

def calculate_temperature_risk(readings_72h):
    """
    readings_72h: list of dicts [{'temp': 24.5}, ...]
    Computes index based on threshold excursions over the last 72 hours.
    Returns: 0 to 100
    """
    total = len(readings_72h)
    if total == 0:
        return 0.0

    excursions = sum(1 for r in readings_72h if r.get('temp') is not None and r['temp'] > TEMP_THRESHOLD_C)
    return (excursions / total) * 100.0

def get_mean_temp_and_humidity(readings_72h):
    """Helper to get means for the ML model inputs from same list."""
    if not readings_72h:
        return 22.0, 50.0, 0
    t_sum = sum(r['temp'] for r in readings_72h if r.get('temp') is not None)
    h_sum = sum(r['humidity'] for r in readings_72h if r.get('humidity') is not None)
    total_t = sum(1 for r in readings_72h if r.get('temp') is not None)
    total_h = sum(1 for r in readings_72h if r.get('humidity') is not None)
    excursions = sum(1 for r in readings_72h if r.get('temp') is not None and r['temp'] > TEMP_THRESHOLD_C)
    
    t_mean = (t_sum / total_t) if total_t > 0 else 22.0
    h_mean = (h_sum / total_h) if total_h > 0 else 50.0
    
    return t_mean, h_mean, excursions

