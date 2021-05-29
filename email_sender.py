import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config

msg = MIMEMultipart()
from_email = 'mels.store.offical@gmail.com'
password = config.admin_password


def send_message(email, subject, message):
    msg.attach(MIMEText(message, 'plain'))
    msg['Subject'] = subject
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, password)
    server.sendmail(from_email, email, msg.as_string())
    server.quit()
