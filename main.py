from motion_detector import MotionDetector
from alert_system import alert


class main:
    def __init__(self):
        self.detector = MotionDetector() 
        self.detector.run()

        self.alert_system = alert()


        