from MotionDetector import MotionDetector
from alert_system import Alarm
from sentryTurret import Sentry
# Play light and sound when motion detected
# figure out step size
# Link Stepper.py to RotatingBase.py
if __name__ == "__main__":
    sentry = Sentry(left_pin=1, right_pin=7, wait_duration=3, rotations_before_switch=8,rotate_duration=.15)
    
    try:
        detector = MotionDetector(sentry=sentry)
        detector.run()
    finally:
        stand.stop()
