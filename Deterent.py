import time
import board       # Provides Raspberry Pi pin names
import digitalio   # Library for digital input/output


class Alarm:
    """
    A class to create a simple alarm system using a sensor, LED, and buzzer
    connected to a Raspberry Pi's GPIO pins via the digitalio library.
    """

    def __init__(self, sensor_pin_id, light_pin_id, sound_pin_id, trigger_state=False, flash_interval=0.5):
        """
        Initializes the Alarm system.

        Args:
            sensor_pin_id: The board pin identifier for the sensor (e.g., board.D17).
            light_pin_id: The board pin identifier for the LED (e.g., board.D27).
            sound_pin_id: The board pin identifier for the buzzer (e.g., board.D22).
            trigger_state (bool): The digital value that indicates the sensor is triggered
                                  (False for LOW, True for HIGH). Defaults to False (trigger on LOW).
                                  Many sensors pull the pin LOW when active, especially with a pull-up.
            flash_interval (float): The interval in seconds for flashing the light/sound.
        """
        print("Initializing Alarm System...")
        self.flash_interval = flash_interval
        self.trigger_state = trigger_state
        self.alarm_active = False
        self.last_toggle_time = 0

        # --- Setup Sensor Pin ---
        try:
            self.sensor_pin = digitalio.DigitalInOut(sensor_pin_id)
            self.sensor_pin.direction = digitalio.Direction.INPUT
            # Set pull-up resistor if triggering on LOW (sensor pulls pin down)
            # Set pull-down resistor if triggering on HIGH (sensor pulls pin up)
            # Set to None if your sensor circuit already has an appropriate pull resistor.
            if self.trigger_state is False: # Trigger on LOW, so use internal pull-up
                 self.sensor_pin.pull = digitalio.Pull.UP
                 print(f"Sensor pin {sensor_pin_id} configured as INPUT with PULL_UP. Triggering on LOW.")
            else: # Trigger on HIGH, so use internal pull-down
                 self.sensor_pin.pull = digitalio.Pull.DOWN
                 print(f"Sensor pin {sensor_pin_id} configured as INPUT with PULL_DOWN. Triggering on HIGH.")
            # If you have an external pull resistor configured, you might use:
            # self.sensor_pin.pull = None
            # print(f"Sensor pin {sensor_pin_id} configured as INPUT with no pull resistor. Triggering on {self.trigger_state}.")


        except Exception as e:
            print(f"Error setting up sensor pin {sensor_pin_id}: {e}")
            raise # Stop execution if pin setup fails

        # --- Setup Light Pin ---
        try:
            self.light_pin = digitalio.DigitalInOut(light_pin_id)
            self.light_pin.direction = digitalio.Direction.OUTPUT
            self.light_pin.value = False # Start with light off
            print(f"Light pin {light_pin_id} configured as OUTPUT.")
        except Exception as e:
            print(f"Error setting up light pin {light_pin_id}: {e}")
            raise

        # --- Setup Sound Pin (Buzzer) ---
        try:
            self.sound_pin = digitalio.DigitalInOut(sound_pin_id)
            self.sound_pin.direction = digitalio.Direction.OUTPUT
            self.sound_pin.value = False # Start with sound off
            print(f"Sound pin {sound_pin_id} configured as OUTPUT.")
        except Exception as e:
            print(f"Error setting up sound pin {sound_pin_id}: {e}")
            raise

        print("Alarm initialization complete.")


    def check_sensor(self):
        """Checks if the sensor is currently in its triggered state."""
        # Reads the pin value and compares it to the expected trigger state
        return self.sensor_pin.value == self.trigger_state

    def _toggle_outputs(self):
        """Toggles the state of the light and sound pins."""
        current_time = time.monotonic()
        if current_time - self.last_toggle_time >= self.flash_interval:
            self.light_pin.value = not self.light_pin.value
            self.sound_pin.value = not self.sound_pin.value # Toggle buzzer for beeping sound
            # If you want a continuous sound instead of beeping:
            # self.sound_pin.value = True
            self.last_toggle_time = current_time

    def run(self):
        """Runs the main alarm loop, checking the sensor and controlling outputs."""
        print("Alarm system running. Press Ctrl+C to exit.")
        try:
            while True:
                if self.check_sensor():
                    # Sensor is triggered
                    if not self.alarm_active:
                        print("ALARM TRIGGERED!")
                        self.alarm_active = True
                        # Reset toggle timer to start flashing immediately
                        self.last_toggle_time = time.monotonic() - self.flash_interval
                        # Ensure outputs start in a known state (e.g., ON) immediately
                        self.light_pin.value = True
                        self.sound_pin.value = True


                    # If alarm is active, toggle the outputs based on interval
                    self._toggle_outputs()

                else:
                    # Sensor is NOT triggered
                    if self.alarm_active:
                        print("Alarm condition cleared. Deactivating.")
                        self.alarm_active = False
                        # Ensure outputs are turned off
                        self.light_pin.value = False
                        self.sound_pin.value = False

                # Small delay to prevent hogging CPU, adjust as needed
                # This delay also affects responsiveness slightly.
                time.sleep(0.05)

        except KeyboardInterrupt:
            print("\nExiting alarm system.")
        finally:
            # --- Cleanup GPIO pins ---
            print("Cleaning up GPIO resources...")
            if hasattr(self, 'light_pin'):
                self.light_pin.value = False # Turn off before deinitializing
                self.light_pin.deinit()
            if hasattr(self, 'sound_pin'):
                self.sound_pin.value = False # Turn off before deinitializing
                self.sound_pin.deinit()
            if hasattr(self, 'sensor_pin'):
                self.sensor_pin.deinit()
            print("GPIO cleanup complete.")
            

# --- Example Usage ---
if __name__ == "__main__":
    # Define your GPIO pins using the board library
    # Common GPIO numbers: D4, D17, D27, D22, D23, D24, D25, D18, etc.
    # Check Raspberry Pi pinout diagrams for `board.Dx` equivalents.
    SENSOR_GPIO = board.D17  # GPIO 17
    LED_GPIO = board.D27     # GPIO 27
    BUZZER_GPIO = board.D22  # GPIO 22

    # --- Configuration ---
    # Does your sensor output LOW (False) or HIGH (True) when triggered?
    # Most PIR sensors with standard connections go LOW when motion detected.
    TRIGGER_ON_LOW = True # Set to False if your sensor goes HIGH when triggered

    FLASH_SPEED_SECONDS = 0.4 # How fast the light/buzzer flash (on/off cycle will be 2*this)

    # Create an instance of the Alarm
    # If TRIGGER_ON_LOW is True, we set trigger_state=False
    # If TRIGGER_ON_LOW is False, we set trigger_state=True
    my_alarm = Alarm(sensor_pin_id=SENSOR_GPIO,
                     light_pin_id=LED_GPIO,
                     sound_pin_id=BUZZER_GPIO,
                     trigger_state=(not TRIGGER_ON_LOW),
                     flash_interval=FLASH_SPEED_SECONDS)

    # Run the alarm system
    my_alarm.run()