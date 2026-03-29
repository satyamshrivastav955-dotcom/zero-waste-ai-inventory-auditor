# Zero-Waste AI Inventory Auditor

A complete end-to-end, offline-first Edge ML prototype designed to monitor and minimize medicinal and food waste using a Raspberry Pi 4.

## Team Assembly Note
> **STOP AND READ `docs/wiring.md` BEFORE TOUCHING ANY HARDWARE.**
> Connecting power incorrectly will permanently destroy the Raspberry Pi and the sensors.

## 1. Hardware Summary
This system relies on precise GPIO integration. For full details, see [wiring.md](wiring.md).
- **Raspberry Pi 4**: Main compute node (Backend + DB + Frontend + ML)
- **DHT22**: Direct GPIO 4 Temp/Hum sensing
- **ESP32 Node**: Remote DHT22 sent via REST over WiFi
- **Load Cell + HX711**: Mass measurement (Sales Velocity Proxy)
- **USB Scanner**: Keyboard HID Barcode reading
- **Status Alerts**: LEDs (GPIO 18), Buzzer (GPIO 23)

## 2. Raspberry Pi OS Setup
Before starting, ensure the Pi is up to date and interfaces are enabled.
```bash
sudo apt update && sudo apt upgrade -y
# Enable interfaces if required for custom HX711 implementations
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0
```

## 3. Python Dependencies
Run these commands to install all required packages:
```bash
pip3 install Flask Flask-Cors pandas numpy scikit-learn
pip3 install RPi.GPIO adafruit-circuitpython-dht
# For the scale:
pip3 install hx711
```

## 4. How to Train the Model
The ML component requires training the Random Forest on initial synthetic distributions.
```bash
python3 backend/ml_model/train_model.py
```
This will output `wps_model.pkl`.

## 5. How to Run the Backend
Start the main orchestration loop (runs background scheduling and Flask API):
```bash
python3 backend/main.py
```

## 6. How to Open the Dashboard
Open the Chromium browser on the Pi and navigate to:
```text
http://localhost:5000/
```

## 7. Configuration & Simulation
By default, the system boots into Simulation Mode. It mocks sensors cleanly so you can test software without hardware hooked up.
- Open `backend/config.py`
- Set `SIMULATION_MODE = False` to engage physical GPIO.

## 8. Step-by-Step Test Sequence
1. Initialize DB: `python scripts/test_api.py` (checks API while `main.py` runs).
2. Train ML: `python scripts/test_ml.py` to ensure WPS handles edge cases.
3. Test Load Cell: `python scripts/test_load_cell.py`.
4. Run Calibration: `python scripts/calibrate_load_cell.py` (place known weight, update ratio).
5. Test DHT22: `python scripts/test_dht22.py`.

## 9. Common Errors & Fixes
- **Error 1**: `ImportError: No module named RPi.GPIO`
  - *Fix*: You're running on a Mac/Windows machine, not a Pi. Set `SIMULATION_MODE = True`.
- **Error 2**: `RuntimeError: DHT sensor not returning data`
  - *Fix*: The DHT22 timing is strict. The script handles this organically natively, just ignore it, or check your 10k resistor pull-up.
- **Error 3**: Load Cell reads negative numbers.
  - *Fix*: Reverse the White (A-) and Green (A+) wires.
- **Error 4**: Model file not found.
  - *Fix*: Run Step 4 (train_model.py) before starting `main.py`.
- **Error 5**: Port 5000 in use.
  - *Fix*: `sudo lsof -i :5000` then `kill -9 <PID>` to close ghost Flask servers.
