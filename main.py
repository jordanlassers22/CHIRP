from motion_detector import MotionDetector
from alert_system import alert
from RotatingBase import RotatingStand
# Play light and sound when motion detected
# figure out step size
# Link Stepper.py to RotatingBase.py
if __name__ == "__main__":
    stand = RotatingStand()

    try:
        detector = MotionDetector(stand=stand)
        detector.run()
    finally:
        stand.stop()
