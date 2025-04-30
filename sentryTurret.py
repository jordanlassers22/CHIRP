import RPi.GPIO as GPIO
import threading
import time

class Sentry:
      """
        A class to manage a rotating sentry turret using GPIO pins on a Raspberry Pi.
        The turret alternates between left and right rotations after a set number of cycles.
        It can be paused/resumed and runs on a background thread.
        Attributes:
            left_pin (int): GPIO pin used to rotate the turret left.
            right_pin (int): GPIO pin used to rotate the turret right.
            rotate_duration (float): Duration in seconds to rotate in one cycle.
            wait_duration (float): Time in seconds to wait between each rotation.
            rotations_before_switch (int): Number of cycles before changing direction.
            isRotating (bool): Flag indicating if the sentry is actively rotating.
        """
    def __init__(self, left_pin=1, right_pin=7, rotate_duration=1, wait_duration=10, rotations_before_switch=5):
        """
        Initialize the Sentry system with the specified GPIO pins and timing configuration.
    
        Args:
            left_pin (int): GPIO pin for rotating left (default: 1).
            right_pin (int): GPIO pin for rotating right (default: 7).
            rotate_duration (float): Duration of each rotation movement (in seconds).
            wait_duration (float): Time to wait between each rotation (in seconds).
            rotations_before_switch (int): Number of rotations before switching direction.
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
        """
        Background thread that handles rotation logic.
        Alternates between rotating left and right based on a cycle count.
        Rotation is paused if `_pause_event` is set and stopped if `_stop_event` is triggered.
        """
            direction = 'left'
            rotation_count = 0

            while not self._stop_event.is_set():
                if not self._pause_event.is_set():
                    self.isRotating = True

                    # Set motor direction
                    if direction == 'left':
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
                        direction = 'right' if direction == 'left' else 'left'
                        rotation_count = 0
                        print(f"Switching direction to {direction}")

                time.sleep(self.wait_duration)


    def pause_rotation(self):
        """
        Pause the turret's rotation. Useful when motion is detected.
        """
        print("Rotation paused")
        self._pause_event.set()

    def resume_rotation(self):
        """
        Resume turret rotation after being paused.
        """
        print("Rotation resumed")
        self._pause_event.clear()

    def stop(self):
        """
        Stop the sentry and clean up all GPIO resources.
        Waits for the background rotation thread to finish.
        """
        self._stop_event.set()
        self._rotation_thread.join()
        GPIO.cleanup()
        
    def __del__(self):
        """
        Destructor to ensure GPIO is cleaned up if the Sentry object is destroyed.
        This provides a safety net in case the `stop()` method wasn't called.
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
