import smtplib
from email.mime.text import MIMEText

# Email details
sender = "chirp.defense.alert@gmail.com"
password = "GoldenEagles22$"  # Use an App Password if 2FA is enabled
receiver = "lassersj@yahoo.com"
subject = "Test Email"
body = "This is a test email sent from Python!"

# Create email
msg = MIMEText(body)
msg["Subject"] = subject
msg["From"] = sender
msg["To"] = receiver

# Send email
with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()  # Enable TLS
    server.login(sender, password)
    server.send_message(msg)

print("Email sent!")