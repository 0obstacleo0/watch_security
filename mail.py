import os
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate


class MailManager:
    def __init__(self):
        self.from_address = os.environ["FROM_ADDRESS"]
        self.to_address = os.environ["TO_ADDRESS"]
        self.to_debug_address = os.environ["TO_DEBUG_ADDRESS"]
        self.password = os.environ["PASSWORD"]

    def send_mail(self, subject, text, debug_flg=False):
        smtpobj = smtplib.SMTP("smtp.gmail.com", 587)
        smtpobj.starttls()
        smtpobj.login(self.from_address, self.password)

        msg = MIMEText(text)
        msg["Subject"] = subject
        msg["From"] = self.from_address
        msg["To"] = self.to_address if (not debug_flg) else self.to_debug_address
        msg["Date"] = formatdate()

        smtpobj.send_message(msg)
        smtpobj.close()
