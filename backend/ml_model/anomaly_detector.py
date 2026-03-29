import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ALPHA_EMA

class SalesVelocityAnomalyDetector:
    def __init__(self, alpha=ALPHA_EMA):
        self.alpha = alpha

    def detect(self, weight_history_kg_timeline):
        """
        weight_history_kg_timeline: list of dicts [{'timestamp': dt, 'weight_kg': val}, ...]
        sorted by timestamp ascending.
        Returns:
            smoothed_velocity (float)
            stagnation_hours (float)
            anomaly_flag (int 0 or 1)
        """
        if not weight_history_kg_timeline:
            return 0.0, 0.0, 0
        
        if len(weight_history_kg_timeline) == 1:
            return 0.0, 0.0, 0

        smoothed_velocity = 0.0
        stagnation_hours = 0.0
        velocity_0_count = 0
        
        from datetime import datetime
        dt_fmt = "%Y-%m-%d %H:%M:%S"

        # parse datetime if it is a string format
        def get_dt(ts):
            if isinstance(ts, str):
                try:
                    return datetime.strptime(ts, dt_fmt)
                except ValueError:
                    # simplistic fallback
                    return datetime.fromisoformat(ts)
            return ts

        velocities = []

        for i in range(1, len(weight_history_kg_timeline)):
            curr_weight = weight_history_kg_timeline[i]['weight_kg']
            prev_weight = weight_history_kg_timeline[i-1]['weight_kg']
            
            # Sale means weight decreased
            current_delta = max(0, prev_weight - curr_weight)
            
            # EMA Update
            if i == 1:
                smoothed_velocity = current_delta
            else:
                smoothed_velocity = self.alpha * current_delta + (1 - self.alpha) * smoothed_velocity
            
            velocities.append(smoothed_velocity)

            dt_curr = get_dt(weight_history_kg_timeline[i]['timestamp'])
            dt_prev = get_dt(weight_history_kg_timeline[i-1]['timestamp'])
            hours_diff = (dt_curr - dt_prev).total_seconds() / 3600.0

            if current_delta == 0:
                stagnation_hours += hours_diff
            else:
                stagnation_hours = 0.0

        anomaly_flag = 0

        # Anomaly Condition 1: Stagnation > 48h
        if stagnation_hours > 48.0:
            anomaly_flag = 1
        
        # Anomaly Condition 2: Drop > 80% vs 7-day avg
        # (Using available velocities, bounded by length)
        if len(velocities) > 7:
            # simple 7-period lookback proxy if each period is e.g. 24h
            # since sensor reads every 6h, 7 days = 28 reads
            lookback = min(len(velocities)-1, 28)
            prev_avg = sum(velocities[-lookback-1:-1]) / lookback
            if prev_avg > 0 and smoothed_velocity < 0.2 * prev_avg:
                anomaly_flag = 1

        return float(smoothed_velocity), float(stagnation_hours), int(anomaly_flag)

# Singleton-like usage
_detector_instance = None
def analyze_velocity(weight_history_kg_timeline):
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = SalesVelocityAnomalyDetector()
    return _detector_instance.detect(weight_history_kg_timeline)
