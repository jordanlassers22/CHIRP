import threading
from time import sleep
from MotorController import MotorController

class RotatingStand:
    
    def __init__(self, pin=18):

        self.ROTATION_DELAY = 100
        self.motorController = MotorController()
        self.isRotating = False
        self.angle = 0
        self.direction = 1  # 1 = clockwise, -1 = counterclockwise
        self.running = True
        self.rotation_paused = False  # Pause rotation when motion is detected
        self.time_between_rotations = 10 # Time device rests before rotating

        # Start rotation in a background thread
        self.thread = threading.Thread(target=self.rotate_loop)
        self.thread.daemon = True
        self.thread.start()

    def setAngle(self, angle):
        self.isRotating = True
        self.angle = angle
        print(f"Rotating to {self.angle}°")
        self.motorController.rotate_degrees(self.angle, self.ROTATION_DELAY)
        self.isRotating = False

    def rotate_loop(self):
        while self.running:
            if self.rotation_paused:
                sleep(1)  # Wait and check again if rotation is paused
                continue
            # Update angle
            self.angle += 15 * self.direction

            # Flip direction if limit reached
            if self.angle >= 180:
                self.angle = 180
                self.direction = -1
            elif self.angle <= 0:
                self.angle = 0
                self.direction = 1

            self.setAngle(self.angle)
            sleep(self.time_between_rotations)  # Wait between rotations

    def pause_rotation(self):
        """Pauses rotation when motion is detected."""
        self.rotation_paused = True

    def resume_rotation(self):
        """Resumes rotation when no motion is detected."""
        self.rotation_paused = False

    def stop(self):
        """Stops the rotation thread."""
        self.running = False
