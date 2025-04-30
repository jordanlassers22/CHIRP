# Chicken Coop Intruder Detection System

## Overview
This project protects a chicken coop from intruders using a Raspberry Pi.  
It uses a camera to detect motion, sounds an alarm when intruders are detected, pauses the camera stand's rotation, and sends an email notification to the owner.  

---

## Features
-  **Motion Detection:** Detects movement using Picamera2 and OpenCV.
-  **Alarm System:** Sounds an alarm immediately when motion is detected.
-  **Sentry Mode:** Automatically pans the camera up to 359° and reverses direction .
-  **Email Notifications:** Sends an email when motion is detected.
-  **Video Recording:** Saves video files of detected motion events.


## How It Works
1. The camera continuously monitors the coop.
2. When motion is detected:
   - An alarm sound is triggered.
   - The camera stand pauses its rotation.
   - (Future) An email alert is sent to the user.
3. When no motion is detected for a period, the camera rotation resumes automatically.
4. All motion events are recorded into a `/recordings/` folder.


## Requirements
- Raspberry Pi (with GPIO support)
- PiCamera2
- OpenCV
- DigitalIO (for motor control)
- Python 3


## Project Structure
```
/recordings/        # Saved video files
MotorController.py  # Controls motor for rotating the camera
RotatingStand.py    # Manages stand rotation logic
MotionDetector.py   # Handles video capture, motion detection, alarm triggering
requirements.md     # Project requirements document
LICENSE             # License file (MIT License)
README.md           # This file
```

---

## License
This project is licensed under the [MIT License](LICENSE).


## Future Improvements
- Improve motion detection sensitivity and configurability.
- Add a web dashboard for remote monitoring.
