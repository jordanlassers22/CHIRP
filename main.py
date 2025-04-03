from motion_detector import MotionDetector
from alert_system import alert
from RotatingBase import RotatingStand

if __name__ == "__main__":
    stand = RotatingStand()

    try:
        detector = MotionDetector(stand=stand)
        detector.run()
    finally:
        stand.stop()
