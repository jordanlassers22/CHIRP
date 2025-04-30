# CHIRP Surveillance System – User Guide

Welcome to the **CHIRP Surveillance System**! This guide will walk you through installing, wiring, and running the system.

---

## Requirements

### Hardware

- Raspberry Pi (Pi 4 recommended)
- PiCamera 2 module
- Buzzer/siren (GPIO-compatible)
- DC motor connected to GPIO pins (for turret rotation)
- Wiring as shown in the wiring diagram (`wiring_diagram.png`)

### Software

- Raspberry Pi OS (Bullseye recommended)
- Python 3.9+
- Required libraries listed below

---

## Installation

1. **Clone the Repository**

```bash
git clone https://github.com/YOUR_USERNAME/CHIRP.git
cd CHIRP
```

2. **Enable Interfaces**
 
```bash
sudo raspi-config
```
Enable Camera Interface
Enable I2C

3. **Install Dependencies**

```bash
sudo apt update
sudo apt install -y python3-pip python3-opencv libcamera-dev
pip3 install numpy RPi.GPIO picamera2
```

## Wiring Installation
Refer to wiring_diagram.png for a full diagram. Basic GPIO usage:
Camera: Connect to CSI port
Alarm: GPIO 16
Motor Control:
Left: GPIO 1
Right: GPIO 7
Use transistors/relays if powering motors with an external source.

## Running the Program
From the project folder:
```bash
python3 main.py
```
This will:
- Start the turret rotation loop
- Begin motion detection
- Pause turret when motion is detected
- Optionally trigger an alarm
- Record video if recording is toggled on

## Keyboard Controls
r	Toggle recording mode
q	Quit the program

Recordings are saved to the recordings/ directory.

## Testing Individual Modules/Components
To test individual components:

Alarm:
```bash
python3 alert_system.py
```

Turret:

```bash
python3 sentryTurret.py
```

Motion Detection (no turret):
```bash
python3 MotionDetector.py
```

## Troubleshooting
Issue	Solution
| Issue                   | Solution                                                                 |
|-------------------------|--------------------------------------------------------------------------|
| *** no cameras available *** | Check ribbon cable, enable camera in raspi-config                    |
| libcamera-hello fails   | Run `sudo modprobe bcm2835-v4l2`, then retry                             |
| Alarm silent            | Verify GPIO pin (16 by default) and active-high/low logic               |
| Motors unresponsive     | Check pin assignments and power delivery                                |
| Script exits instantly  | Confirm camera is detected and run from an interactive shell            |
| High CPU usage          | Script auto-detects headless mode to reduce load                        |

## Cleanup
When quitting (Ctrl+C or q), all GPIO and camera resources should be released. If pins behave oddly, you can reboot:
```bash
sudo reboot
```

## Notes
- Recording is off by default. Press r to start recording when motion is detected.
- The system supports headless operation over SSH by setting QT_QPA_PLATFORM=offscreen.

