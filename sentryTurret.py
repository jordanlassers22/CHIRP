import RPi.GPIO as GPIO
import threading
import time

class Sentry:
    def __init__(self, left_pin=1, right_pin=7, rotate_duration=1, wait_duration=10, rotations_before_switch=5):
        """
        :param left_pin: GPIO pin number to rotate left
        :param right_pin: GPIO pin number to rotate right
        :param rotate_duration: Time in seconds to rotate each cycle
        :param wait_duration: Time in seconds to wait between rotations
        :param rotations_before_switch: Number of rotations before changing direction
        """
        self.left_pin = left_pin
        self.right_pin = right_pin
        self.rotate_duration = rotate_duration
        self.wait_duration = wait_duration
        self.rotations_before_switch = rotations_before_switch

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.left_pin, GPIO.OUT)
        GPIO.setup(self.right_pin, GPIO.OUT)

        self.isRotating = False
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._rotation_thread = threading.Thread(target=self._rotate_loop)
        self._rotation_thread.daemon = True
        self._rotation_thread.start()

    def _rotate_loop(self):
            direction = 'right'
            rotation_count = 0

            while not self._stop_event.is_set():
                if not self._pause_event.is_set():
                    self.isRotating = True

                    # Set motor direction
                    if direction == 'right':
                        GPIO.output(self.right_pin, GPIO.HIGH)
                        GPIO.output(self.left_pin, GPIO.LOW)
                    else:
                        GPIO.output(self.left_pin, GPIO.HIGH)
                        GPIO.output(self.right_pin, GPIO.LOW)

                    print(f"Rotating {direction} for {self.rotate_duration} seconds")
                    time.sleep(self.rotate_duration)

                    # SAFETY: Always stop motor before anything else
                    GPIO.output(self.left_pin, GPIO.LOW)
                    GPIO.output(self.right_pin, GPIO.LOW)
                    self.isRotating = False

                    # SAFETY: Tiny delay to ensure motor fully stops
                    time.sleep(0.05)  # 50 milliseconds pause

                    rotation_count += 1

                    # Switch direction after specified number of rotations
                    if rotation_count >= self.rotations_before_switch:
                        direction = 'left' if direction == 'right' else 'right'
                        rotation_count = 0
                        print(f"Switching direction to {direction}")

                time.sleep(self.wait_duration)


    def pause_rotation(self):
        """Pause the stand rotation."""
        print("Rotation paused")
        self._pause_event.set()

    def resume_rotation(self):
        """Resume the stand rotation."""
        print("Rotation resumed")
        self._pause_event.clear()

    def stop(self):
        """Stop rotation and clean up GPIO."""
        self._stop_event.set()
        self._rotation_thread.join()
        GPIO.cleanup()
        
    def __del__(self):
        """
        Destructor: Make sure GPIO is cleaned up if the object is deleted.
        """
        print("Destructor called, cleaning up GPIO...")
        try:
            self.stop()
        except Exception as e:
            print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    try:
        # Create the sentry stand 
        stand = Sentry(left_pin=1, right_pin=7, wait_duration=3, rotations_before_switch=8,rotate_duration=.15)

        print("Sentry stand is running. Press CTRL+C to stop.")
        while True:
            time.sleep(1)  # Just keep the main thread alive

    except KeyboardInterrupt:
        print("Keyboard Interrupt detected. Exiting...")

    finally:
        if 'stand' in locals():
            stand.stop()
