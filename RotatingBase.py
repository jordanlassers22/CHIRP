import threading
from time import sleep
class RotatingStand:
    
    def __init__(self, pin=18):
        self.isRotating = False
        self.angle = 0
        self.direction = 1  # 1 = clockwise, -1 = counterclockwise
        self.running = True
        self.rotation_paused = False # Pause rotation

        # Start rotation in a background thread
        self.thread = threading.Thread(target=self.rotate_loop)
        self.thread.daemon = True
        self.thread.start()

    def setAngle(self, angle):
        self.isRotating = True
        self.angle = angle
        print(f"Rotating to {self.angle}°")
        sleep(4)  # Simulate time to rotate
        self.isRotating = False

    def rotate_loop(self):
        while self.running:
            if self.rotation_paused:
                sleep(1)  # wait briefly and check again
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
            sleep(3)  # Wait between rotations

    def pause_rotation(self):
        self.rotation_paused = True

    def resume_rotation(self):
        self.rotation_paused = False

    def stop(self):
        self.running = False
