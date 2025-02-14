import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from copy import deepcopy
from cost_table import CostTable
import os


class EmailWrapper:
    def __init__(self, mail_template):
        self.sender_email = "charles@fakemail.me"
        self.password = input("Type your password and press enter:")
        template_file = open(mail_template, 'r')
        self.message_template = template_file.read()
        template_file.close()
        self.subject = "[ACP FakeName] Decompte de charges %TITLE%"

    def get_email_text(self, table: CostTable, owner: str):
        text = deepcopy(self.message_template)
        text = text.replace('%TITLE%', table.get_report_title())
        text = text.replace('%AMOUNT%', table.get_owner_total(owner))
        text = text.replace('%NAME%', table.get_owner_name(owner))
        return text

    def get_subject(self, table: CostTable):
        text = deepcopy(self.subject)
        text = text.replace('%TITLE%', table.get_report_title())
        return text

    def send_email(self, table: CostTable, owner: str, filename):
        # Create a multipart message and set headers
        to_email = table.get_owner_email(owner)
        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = to_email[0]
        message["Subject"] = self.get_subject(table)
        if len(to_email) > 1:
            bcc = to_email[1]
            for e in range(2, len(to_email)):
                bcc += ', '
                bcc += to_email[e]
            message["Bcc"] = bcc

        # Add body to email
        message.attach(MIMEText(self.get_email_text(table, owner), "plain"))

        # Open PDF file in binary mode
        with open(filename, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {os.path.basename(filename)}",
        )

        # Add attachment to message and convert message to string
        message.attach(part)
        text = message.as_string()

        # Log in to server using secure context and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.mail.ovh.net", 465, context=context) as server:
            server.login(self.sender_email, self.password)
            server.sendmail(self.sender_email, to_email[0], text)