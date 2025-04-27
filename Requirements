# Chicken Coop Intruder Detection System

## Overview
This project protects a chicken coop from intruders.  
It uses a camera for motion detection, plays an audible alarm when motion is detected, rotates the camera using a motorized stand, and sends a notification to the user via email.

---

## Feature 1: Motion Detection and Alarm System

### Functional Requirements (FR)
- The system will capture video using a camera.
- The system will detect motion by comparing the current video frame to a reference frame.
- When motion is detected, the system will:
  - Play an alarm sound.
  - Pause the camera rotation.
  - Display a box around the detected motion area.

### Non-Functional Requirements (NFR)
- The motion detection will trigger within 1 second of detecting motion.
- The alarm must sound once motion is detected.
### Acceptance Criteria (AC)
- When an object moves into the camera’s field of view, the alarm will sound within 1 second.
- When no motion is detected for 100 consecutive frames, the alarm must stop and camera rotation must resume.


## Feature 2: Rotating Camera Stand

### Functional Requirements (FR)
- The stand will rotate the camera 15 degrees every 10 seconds.
- If the rotation reaches 180 degrees, it will reverse direction until it returns to 0 degrees.
- The stand will pause rotation during detected motion and resume when motion stops.

### Non-Functional Requirements (NFR)
- Motor movement will occur smoothly without jerky motion.

### Acceptance Criteria (AC)
- The stand must pause rotation during active motion detection and resume 3 seconds after motion stops.
- The stand must reverse rotation direction after reaching 0° and 180° limits.


## Feature 3: Email Notification System (Planned Future Addition)

### Functional Requirements (FR)
- Upon detecting motion, the system will send an email notification to a predefined email address.

### Non-Functional Requirements (NFR)
- The email must be sent within 5 seconds of confirmed motion detection.
- Email delivery must include a timestamp and a "Motion detected!" message.

### Acceptance Criteria (AC)
- After a test trigger, the user must receive an email notification within 5 seconds, 9 out of 10 times.
