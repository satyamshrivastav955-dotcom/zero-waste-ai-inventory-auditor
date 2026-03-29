import os

# Base Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'database', 'inventory.db')
MODEL_PATH = os.path.join(BASE_DIR, 'backend', 'ml_model', 'wps_model.pkl')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Simulation Toggle
SIMULATION_MODE = True

# GPIO Pins configuration (BCM)
PIN_DHT22_1 = 4
PIN_DHT22_2 = 17 # Optional if using ESP32 instead
PIN_HX711_DOUT = 5
PIN_HX711_SCK = 6
PIN_LED_SAFE = 18 
PIN_LED_WARN = 18 # We can use one RGB LED or separate, using 18 for demo as per prompt red/yellow map
PIN_LED_CRITICAL = 18 
PIN_BUZZER = 23

# System thresholds
TEMP_THRESHOLD_C = 25.0
STAGNATION_HOURS_MAX = 168.0

# Intervals
SENSOR_READ_INTERVAL_HOURS = 6

# Constants
ALPHA_EMA = 0.3
