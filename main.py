"""
main.py
Main method for the CHIRP Surveillance System. This script initializes the sentry turret
and motion detection system, then runs them in coordination. When motion is detected,
the turret is paused and other actions like alarms or recordings may be triggered.

Modules:
    - MotionDetector: Handles camera input and motion detection logic.
    - Sentry: Controls the rotating turret platform via GPIO.
"""
from MotionDetector import MotionDetector
from sentryTurret import Sentry
if __name__ == "__main__":
    sentry = Sentry(left_pin=1, right_pin=7, wait_duration=3, rotations_before_switch=8,rotate_duration=.15)
    try:
        # Initialize the motion detector and inject the sentry so it can pause/resume rotation
        detector = MotionDetector(sentry=sentry)
        detector.run() # Begin motion detection loop
    except KeyboardInterrupt: # Dxit on Ctrl+C
        print("KeyboardInterrupt received. Exiting cleanly...")
    finally:
        sentry.stop() # Ensure sentry turret is properly stopped and GPIO pins are cleaned


