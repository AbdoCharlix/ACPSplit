import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from copy import deepcopy
from cost_table import CostTable
import os


class EmailWrapper:
    def __init__(self, mail_template, mail_config):
        # We populate global email variable from config file
        self.sender_id = mail_config['sender_id']
        self.sender_email = mail_config['sender_email']
        self.config = mail_config
        self.subject = mail_config['subject']
        self.smtp_server = mail_config['smtp_server']
        self.smtp_port = int(mail_config['smtp_port'])
        self.password = input("Type your password and press enter:")

        # Read template file
        template_file = open(mail_template, 'r')
        self.message_template = template_file.read()
        template_file.close()

    def get_email_text(self, table: CostTable, owner: str):
        text = deepcopy(self.message_template)
        # Replace some strings to personalize email text
        text = text.replace('_TITLE_', table.get_report_title())
        text = text.replace('_AMOUNT_', table.get_owner_total(owner))
        text = text.replace('_NAME_', table.get_owner_name(owner))
        # We raplace any key starting with _ in config.ini for more freedom in email template
        for key in self.config:
            if key[0] == '_':
                text = text.replace(key, self.config[key])
        return text

    def get_subject(self, table: CostTable):
        text = deepcopy(self.subject)
        text = text.replace('_TITLE_', table.get_report_title())
        return text

    def send_email(self, table: CostTable, owner: str, filename):
        # Create a multipart message and set headers
        # Send for each recipient in email list
        to_email = table.get_owner_email(owner)
        for e in to_email:
            message = MIMEMultipart()
            message["From"] = self.sender_id
            message["To"] = e
            message["Subject"] = self.get_subject(table)

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
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                server.login(self.sender_email, self.password)
                server.sendmail(self.sender_email, e, text)