import RPi.GPIO as GPIO
import time

class Alarm:
    def __init__(self, pin=16, active_high=True):
        """
        Initialize the alarm on a given GPIO pin.
        :param pin: GPIO pin number (BCM mode)
        :param active_high: True if alarm is activated by HIGH signal, False for active-low
        """
        self.pin = pin
        self.active_state = GPIO.HIGH if active_high else GPIO.LOW
        self.inactive_state = GPIO.LOW if active_high else GPIO.HIGH

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, self.inactive_state)

    def sound_for(self, duration=2, repeats=1):
            for _ in range(repeats):
                print(f"Alarm ON for {duration} seconds")
                GPIO.output(self.pin, self.active_state)
                time.sleep(duration)
                GPIO.output(self.pin, self.inactive_state)
                print("Alarm OFF")
                time.sleep(1)  # pause


    def cleanup(self):
        """
        Clean up GPIO settings (optional call at program end)
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

    
