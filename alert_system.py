import RPi.GPIO as GPIO
import time

class Alarm:
    """
        A class to manage a GPIO-controlled alarm such as a buzzer or siren.
        Attributes:
            pin (int): The GPIO pin number to which the alarm is connected (BCM mode).
            active_state (int): GPIO.HIGH or GPIO.LOW depending on wiring (active-high or active-low).
            inactive_state (int): Opposite of active_state to turn off the alarm.
        """
    def __init__(self, pin=16, active_high=True):
        """
        Initialize the alarm on a given GPIO pin.
        Args:
            pin (int): The GPIO pin number using BCM numbering.
            active_high (bool): If True, GPIO.HIGH activates the alarm (default). Use False for active-low alarms.
        """
        self.pin = pin
        self.active_state = GPIO.HIGH if active_high else GPIO.LOW
        self.inactive_state = GPIO.LOW if active_high else GPIO.HIGH

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, self.inactive_state)

    def sound_for(self, duration=2, repeats=1):
        """
        Activate the alarm for a specified duration and number of repeats.
        Args:
            duration (float): Time in seconds the alarm should stay on per cycle.
            repeats (int): Number of times to repeat the alarm cycle.
        """
            for _ in range(repeats):
                print(f"Alarm ON for {duration} seconds")
                GPIO.output(self.pin, self.active_state)
                time.sleep(duration)
                GPIO.output(self.pin, self.inactive_state)
                print("Alarm OFF")
                time.sleep(1)  # pause


    def cleanup(self):
        """
        Clean up GPIO settings. Should be called at the end of your program to safely release GPIO pins.
        """
        GPIO.cleanup()

# Example usage
if __name__ == "__main__":
        alarm = Alarm(pin=16, active_high=True)  # Set active_high=False if it’s active-low
        alarm.sound_for(2, 2)
        alarm.cleanup()

"""
import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv


class Email:
    def __init__(self):
        load_dotenv()
        self.user = os.environ["EMAIL_ADDRESS"]
        self.pw = os.environ["EMAIL_PASSWORD"]


    def email(self, subject, body, recepient):

        msg = EmailMessage()
        msg['subject'] = subject
        msg['to'] = recepient
        msg['from'] = self.user
        msg.set_content(body)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(self.user, self.pw)
        server.send_message(msg)
        server.quit()
"""

    
