import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv


class alert:
    def __init__(self):
        load_dotenv()
        self.user = os.environ["EMAIL_ADDRESS"]
        self.pw = os.environ["EMAIL_PASSWORD"]


    def alert(self, subject, body, recepient):

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



if __name__ == "__main__":
    sms_alert = alert()
    sms_alert.alert("Hello", "This is test", "csvaughan14@gmail.com")