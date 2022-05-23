import json
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate

json_file = open("settings.json", "r")
json_data = json.load(json_file)

FROM_ADDRESS = json_data["FROM_ADDRESS"]
TO_ADDRESS = json_data["TO_ADDRESS"]
PASSWORD = json_data["PASSWORD"]


# メール送信
def send_mail(subject, text):
    smtpobj = smtplib.SMTP("smtp.gmail.com", 587)
    smtpobj.starttls()
    smtpobj.login(FROM_ADDRESS, PASSWORD)

    msg = MIMEText(text)
    msg["Subject"] = subject
    msg["From"] = FROM_ADDRESS
    msg["To"] = TO_ADDRESS
    msg["Date"] = formatdate()

    smtpobj.send_message(msg)
    smtpobj.close()
