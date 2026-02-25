# 💧 Smart Water Quality Monitoring System

A Raspberry Pi-based IoT system that continuously monitors water quality in real time using environmental sensors, with access control managed through RFID authentication and a keypad interface. Built as a hardware-software integration project using Python.

---

## 📌 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Hardware Components](#hardware-components)
- [System Architecture](#system-architecture)
- [How It Works](#how-it-works)
- [Getting Started](#getting-started)
- [Wiring Guide](#wiring-guide)
- [Running the System](#running-the-system)
- [Project Structure](#project-structure)
- [License](#license)

---

## Overview

Access to clean water is a critical public health concern. Manual water quality testing is time-consuming and requires specialist equipment. This system automates real-time water quality monitoring by integrating a Raspberry Pi with environmental sensors, and restricts system access to authorised users via RFID card scanning and keypad PIN entry — making it suitable for deployment in controlled environments such as labs, water treatment facilities, or research settings.

---

## Features

- 🌡️ **Real-time environmental sensing** — continuously reads temperature and humidity data using the DHT11 sensor
- 💳 **RFID access control** — only authorised RFID cards can activate the monitoring system
- 🔢 **Keypad PIN entry** — secondary authentication layer via physical keypad
- 📊 **Live data display** — sensor readings displayed in real time via terminal or connected display
- 🐍 **Single-file Python implementation** — clean, readable code in `Project_Final.py`
- 🔒 **MIT Licensed** — open source and free to use

---

## Hardware Components

| Component | Purpose |
|-----------|---------|
| **Raspberry Pi** (3B+ or 4 recommended) | Main processing unit |
| **DHT11 Sensor** | Measures temperature and humidity |
| **RFID Reader (RC522)** | Reads RFID cards for access control |
| **RFID Cards / Tags** | Authorised user credentials |
| **4x4 Matrix Keypad** | PIN entry for secondary authentication |
| **Jumper wires** | GPIO connections |
| **Breadboard** | Circuit prototyping |
| **Power supply** | 5V micro-USB for Raspberry Pi |

---

## System Architecture

```
┌─────────────────────────────────────────────┐
│               Raspberry Pi                  │
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  DHT11   │  │  RC522   │  │  Keypad  │  │
│  │  Sensor  │  │   RFID   │  │  (4x4)   │  │
│  │          │  │  Reader  │  │          │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│       │              │              │        │
│       └──────────────┴──────────────┘        │
│                      │                       │
│              Python (Project_Final.py)        │
│                      │                       │
│              Real-time data output            │
│          (terminal / display / logs)          │
└─────────────────────────────────────────────┘
```

**Authentication flow:**
1. User scans RFID card → system checks against authorised card list
2. If authorised → prompts for keypad PIN
3. If PIN correct → monitoring system activates and begins live sensor readings
4. Sensor data is continuously read and displayed

---

## How It Works

### Access Control
The system uses a **two-factor authentication** approach:
- **Factor 1 — RFID:** The RC522 RFID reader scans a card. The card's unique ID is checked against a list of pre-authorised IDs stored in the script.
- **Factor 2 — Keypad:** After successful RFID scan, the user enters a PIN on the 4x4 matrix keypad. Both must match for access to be granted.

### Water Quality Monitoring
Once authenticated, the **DHT11 sensor** begins polling and outputs:
- **Temperature** (°C) — elevated temperatures can indicate biological activity or contamination
- **Humidity** (%) — relevant for environmental context and sensor calibration

Readings are captured continuously and displayed in the terminal. The system can be extended to log readings to a file or transmit them over a network.

---

## Getting Started

### Prerequisites

- Raspberry Pi (any model with GPIO pins) running **Raspberry Pi OS**
- Python 3.7+
- Internet connection for installing libraries (first-time setup only)

### Install Required Python Libraries

Open a terminal on your Raspberry Pi and run:

```bash
pip3 install RPi.GPIO
pip3 install Adafruit_DHT
pip3 install mfrc522
```

> **Note:** `Adafruit_DHT` requires the C compiler. If you get errors, run:
> ```bash
> sudo apt-get install python3-dev
> pip3 install Adafruit_DHT
> ```

### Clone the Repository

```bash
git clone https://github.com/ZoyaMuneeb/Smart-Water-Quality-Monitoring-System.git
cd Smart-Water-Quality-Monitoring-System
```

---

## Wiring Guide

### DHT11 Sensor → Raspberry Pi GPIO

| DHT11 Pin | Raspberry Pi Pin |
|-----------|-----------------|
| VCC       | 3.3V (Pin 1)    |
| GND       | GND (Pin 6)     |
| DATA      | GPIO 4 (Pin 7)  |

### RC522 RFID Reader → Raspberry Pi GPIO

| RC522 Pin | Raspberry Pi Pin |
|-----------|-----------------|
| VCC       | 3.3V (Pin 1)    |
| GND       | GND (Pin 6)     |
| RST       | GPIO 25 (Pin 22)|
| SDA (SS)  | GPIO 8 (Pin 24) |
| MOSI      | GPIO 10 (Pin 19)|
| MISO      | GPIO 9 (Pin 21) |
| SCK       | GPIO 11 (Pin 23)|

### 4x4 Keypad → Raspberry Pi GPIO

Connect the 8 keypad pins to available GPIO pins as defined in `Project_Final.py`. The default row/column pin mapping is set in the script — check the top of the file for the exact configuration and adjust to match your wiring.

> ⚠️ **Always double-check your wiring before powering on.** Incorrect wiring can damage your Raspberry Pi GPIO pins.

---

## Running the System

```bash
python3 Project_Final.py
```

**Expected behaviour:**
1. System initialises and waits for RFID scan
2. Scan your authorised RFID card
3. Enter your PIN on the keypad when prompted
4. On successful authentication, the terminal begins displaying live sensor readings:
   ```
   Temperature: 24.5°C   Humidity: 60%
   Temperature: 24.6°C   Humidity: 61%
   ...
   ```
5. Press `Ctrl + C` to stop the monitoring loop

### Running on Boot (Optional)

To start the system automatically when the Raspberry Pi powers on:

```bash
sudo nano /etc/rc.local
```

Add this line before `exit 0`:
```bash
python3 /home/pi/Smart-Water-Quality-Monitoring-System/Project_Final.py &
```

Save and exit (`Ctrl + X`, then `Y`, then `Enter`).

---

## Project Structure

```
Smart-Water-Quality-Monitoring-System/
│
├── Project_Final.py    # Main Python script — full system implementation
├── LICENSE             # MIT License
└── README.md           # This file
```

---

## Troubleshooting

**`RuntimeError: Failed to add edge detection`**
→ Another process is using the GPIO pins. Run `sudo pkill python3` and try again.

**DHT11 returns `None` values**
→ Check your wiring. The DHT11 data pin must have a 10kΩ pull-up resistor between DATA and VCC, or use a DHT11 module (which has one built in).

**RFID reader not detecting cards**
→ Make sure SPI is enabled on your Raspberry Pi. Go to `sudo raspi-config` → Interfacing Options → SPI → Enable.

**Keypad not responding**
→ Verify GPIO pin assignments in the script match your physical wiring.

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## Developer

**Zoya Muneeb**  
Computer Engineering Graduate, American University of Sharjah  
[linkedin.com/in/zoya-muneeb](https://www.linkedin.com/in/zoya-muneeb/) · [github.com/ZoyaMuneeb](https://github.com/ZoyaMuneeb)
