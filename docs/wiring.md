# Hardware Wiring Reference for Zero-Waste AI Inventory Auditor

This document is the **official wiring guide** for assembling the prototype hardware. Follow the steps explicitly to prevent damage to the Raspberry Pi 4 and the connected components.

---

## 1. DHT22 Temperature & Humidity Sensor #1 (Local Pi Node)
- **Component**: AM2302 (DHT22) 
- **Resistor Required**: 10kΩ pull-up resistor between VCC and DATA (unless using a pre-mounted breakout board with built-in pull-up).

**Connections:**
- [VCC/VDD] → [3V3 Power] (Physical Pin 1)
- [DATA/OUT] → [GPIO 4] (Physical Pin 7)
- [NC] → Do not connect
- [GND] → [Ground] (Physical Pin 6)

> **COMMON MISTAKE**: Connecting Data to a non-GPIO pin (e.g., physical pin 4 instead of GPIO 4/pin 7).
> **DO NOT**: Never connect the DHT22 VCC to the Pi's 5V pin. It sends 5V back on the data line and will permanently damage the Pi's 3.3V GPIO logic.

---

## 2. DHT22 Temperature & Humidity Sensor #2 (ESP32 Remote Node)
- **Component**: AM2302 (DHT22) connected to ESP32 (30-pin variant)
- **Resistor Required**: 10kΩ pull-up resistor (if naked sensor).

**Connections:**
- [VCC/VDD] → [3V3] (ESP32 3.3V Pin)
- [DATA/OUT] → [GPIO 4] (ESP32 D4 Pin)
- [GND] → [GND] (ESP32 GND Pin)

> **COMMON MISTAKE**: Using the Vin pin for power. Use the regulated 3.3V pin.
> **DO NOT**: Do not hardwire the ESP32 to the Pi; data transmission is over WiFi.

---

## 3. Load Cell (5kg) to HX711 Breakout Board
- **Component**: 4-Wire Aluminum Load Cell (5kg) & IC HX711 

**Connections:**
- [Red Wire] → [E+] (Excitation Plus)
- [Black Wire] → [E-] (Excitation Minus)
- [White Wire] → [A-] (Signal Minus)
- [Green Wire] → [A+] (Signal Plus)

> **COMMON MISTAKE**: Reversing White and Green wires, which leads to negative weight values.
> **DO NOT**: Do not cut the load cell wires too short; they are difficult to re-strip and solder.

---

## 4. HX711 Breakout Board to Raspberry Pi
- **Component**: IC HX711

**Connections:**
- [VCC] → [5V Power] (Physical Pin 2)  *(Check HX711 spec; some boards run on 3.3V. If logic level is standard, 5V powers the chip but it outputs 5V logic. If you are extremely careful, power VCC with 3.3V [Pin 1] to keep data lines at 3.3V safe logic levels.)*
	- *RECOMMENDED:* [VCC] → [3V3 Power] (Physical Pin 1) (to guarantee 3.3V logic)
- [GND] → [Ground] (Physical Pin 9)
- [DT/DOUT] → [GPIO 5] (Physical Pin 29)
- [SCK/CLK] → [GPIO 6] (Physical Pin 31)

> **COMMON MISTAKE**: Connecting VCC to 5V but sending 5V signals directly to the 3.3V Pi GPIO. It's safer to power the HX711 with 3.3V.
> **DO NOT**: Don't power the load cell system from a flaky breadboard rail. Connect directly.

---

## 5. Status LED (Multi-state Warning)
- **Component**: Standard 5mm LEDs (Red/Yellow/Green) or an RGB module.
- **Resistor Required**: 330Ω resistor placed in series with the positive (longer) leg of each LED.

**Connections (Demo uses 1 generalized pin):**
- [Anode / Long Leg] → [via 330Ω Resistor] → [GPIO 18] (Physical Pin 12)
- [Cathode / Short Leg] → [Ground] (Physical Pin 14)

> **COMMON MISTAKE**: Forgetting the resistor, causing the LED to draw too much current and potentially fry the GPIO pin.
> **DO NOT**: Do not connect the LED directly across the 5V and GND pins.

---

## 6. Active Buzzer
- **Component**: 3V or 5V Active Piezo Buzzer (Active meaning it beeps natively on DC current).

**Connections:**
- [VCC / Positive / Long Pin] → [GPIO 23] (Physical Pin 16)
- [GND / Negative/ Short Pin] → [Ground] (Physical Pin 20)

> **COMMON MISTAKE**: Using a passive buzzer, which will just make a tiny "click" sound instead of a continuous beep. Active buzzer is required.
> **DO NOT**: Do not apply reverse polarity.

---

## 7. ESP32 to Raspberry Pi
- **Component**: ESP32 NodeMCU
- **Connection**: WiFi only.
- Configure ESP32 code to point to the Raspberry Pi's local network IP on port 5000. No physical wires between Pi and ESP32.

---

## 8. USB Barcode Scanner
- **Component**: Standard USB HID Barcode / QR Scanner
- **Connection**: Plug into any of the 4 USB Type-A ports on the Raspberry Pi.

> **COMMON MISTAKE**: Assuming complex drivers are needed. It acts as a standard keyboard.
> **DO NOT**: Do not plug into a damaged USB port or force the connector.

---

## VOLTAGE REFERENCE TABLE

| Component | Operating Voltage | Pi Pin Source | Current Draw (Est.) |
| :--- | :--- | :--- | :--- |
| DHT22 | 3.3V | Pin 1 or 17 | 1-2mA |
| HX711 | 3.3V (Recommended) | Pin 1 or 17 | ~2mA |
| LED | Logic High (3.3V via GPIO) | GPIO (e.g. Pin 12) | 10-20mA |
| Buzzer | Logic High (3.3V via GPIO) | GPIO (e.g. Pin 16) | ~30mA |
| Scanner | 5V | USB Port | 100-200mA |

---

## QUICK ASSEMBLY CHECKLIST

Follow this exact order to build the prototype safely:

1. **Power Off**: Ensure the Raspberry Pi power supply is unplugged.
2. **Grounding**: Connect all GND wires to the Pi's ground pins first.
3. **DHT22 Setup**: Connect DHT22 VCC to 3.3V and DATA to GPIO 4. Double-check you aren't using 5V.
4. **Load Cell to HX711**: Connect the 4 wires from Load Cell to the HX711 board explicitly matching the color code (Red E+, Black E-, White A-, Green A+).
5. **HX711 to Pi**: Connect HX711 VCC to 3.3V, GND to GND, and Data lines to GPIO 5 & 6.
6. **Alert System**: Put resistors on LEDs, connect LEDs and Buzzer to respective GPIOs.
7. **Visual Audit**: Trace every red wire. Make absolutely sure no 5V pin goes anywhere near a generic GPIO or a 3.3V rated sensor.
8. **USB Plug**: Plug in the USB Barcode Scanner.
9. **Final Power**: Plug in the USB-C power adapter into the Raspberry Pi 4. Let it boot up.
