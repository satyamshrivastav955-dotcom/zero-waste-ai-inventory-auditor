import os
import sys
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SIMULATION_MODE, LOGS_DIR, PIN_LED_SAFE, PIN_LED_WARN, PIN_LED_CRITICAL, PIN_BUZZER
from database.db_queries import insert_action, insert_wps_result

if not SIMULATION_MODE:
    import RPi.GPIO as GPIO

# Ensure log directory
os.makedirs(LOGS_DIR, exist_ok=True)
ACTIONS_LOG = os.path.join(LOGS_DIR, 'actions.log')

def _log_to_file(msg):
    with open(ACTIONS_LOG, 'a') as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")
    print(msg)

def trigger_hardware_alert(wps_status):
    if SIMULATION_MODE:
        return
        
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup([PIN_LED_SAFE, PIN_LED_WARN, PIN_LED_CRITICAL, PIN_BUZZER], GPIO.OUT)

    # Turn all off initially
    GPIO.output(PIN_LED_SAFE, GPIO.LOW)
    GPIO.output(PIN_LED_WARN, GPIO.LOW)
    GPIO.output(PIN_LED_CRITICAL, GPIO.LOW)
    GPIO.output(PIN_BUZZER, GPIO.LOW)

    if wps_status == "Safe":
        GPIO.output(PIN_LED_SAFE, GPIO.HIGH)
    elif wps_status in ["Markdown", "Bundle"]:
        GPIO.output(PIN_LED_WARN, GPIO.HIGH)
    elif wps_status in ["Donation", "Critical"]:
        GPIO.output(PIN_LED_CRITICAL, GPIO.HIGH)
        # 3 Beeps
        for _ in range(3):
            GPIO.output(PIN_BUZZER, GPIO.HIGH)
            time.sleep(0.3)
            GPIO.output(PIN_BUZZER, GPIO.LOW)
            time.sleep(0.3)
    elif wps_status == "Waste":
        GPIO.output(PIN_LED_CRITICAL, GPIO.HIGH)
        # Continuous 5s beep
        GPIO.output(PIN_BUZZER, GPIO.HIGH)
        time.sleep(5)
        GPIO.output(PIN_BUZZER, GPIO.LOW)

def calculate_wps(days_to_expiry, ml_prob, temp_risk_index, stagnation_hours, product_id, product_name):
    # Step 1: Expiry Factor
    if days_to_expiry <= 0:
        expiry_factor = 1.0
    elif days_to_expiry <= 7:
        expiry_factor = 0.9
    elif days_to_expiry <= 30:
        expiry_factor = 0.6
    elif days_to_expiry <= 90:
        expiry_factor = 0.3
    else:
        expiry_factor = 0.1

    # Step 2: ML Probability -> ml_prob passed directly

    # Step 3: Temperature Risk
    temp_risk = temp_risk_index / 100.0

    # Step 4: Stagnation Penalty
    stagnation_penalty = min(stagnation_hours / 168.0, 1.0)

    # Step 5: Final WPS
    wps = (0.35 * ml_prob +
           0.30 * expiry_factor +
           0.20 * temp_risk +
           0.15 * stagnation_penalty) * 100.0
    
    wps = max(0.0, min(100.0, wps))

    # Status mapping
    if wps < 40:
        status = "Safe"
        action = "SAFE"
    elif wps < 60:
        status = "Markdown"
        action = "MARKDOWN_SUGGESTED"
    elif wps < 80:
        status = "Bundle"
        action = "BUNDLE_SUGGESTED"
    elif wps < 100:
        status = "Critical"  # Donation / Critical
        action = "DONATION_ALERT"
    else:
        status = "Waste"
        action = "WASTE_RECORDED"

    ts = datetime.now().isoformat()
    
    # Save to SQLite
    insert_wps_result(product_id, ts, ml_prob, expiry_factor, temp_risk, stagnation_penalty, wps, status)
    insert_action(product_id, ts, wps, action, f"{product_name} evaluated.")

    # Log text to file & console
    log_msg = f"Product: {product_name} | WPS: {wps:.2f} | Status: {status} | Action: {action}"
    _log_to_file(log_msg)

    # Trigger GPIO
    trigger_hardware_alert(status)

    return {
        'wps': wps,
        'status': status,
        'action': action,
        'components': {
            'ml_prob': ml_prob,
            'expiry_factor': expiry_factor,
            'temp_risk': temp_risk,
            'stagnation_penalty': stagnation_penalty
        }
    }
