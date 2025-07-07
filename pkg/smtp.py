import logging
import smtplib
import time
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class SMTPClient:
    def __init__(self, smtp_server : str, port : int, smtp_user : str, smtp_pass : str):
        self.smtp_server = smtp_server
        self.port = port
        self.smtp_user = smtp_user
        self.smtp_pass = smtp_pass

    def send_email(self, subject, sender_email, receivers_email, body, cc=None, attachments=None, max_retries=3, retry_delay=5):
        logging.info("Preparing to send email with params to: {}, cc: {}, config: {}".format(
            receivers_email, cc, {
                "smtp server": self.smtp_server,
                "port": self.port,
                "username": self.smtp_user,
                "password": self.smtp_pass,
            }
        ))

        attempt = 0
        while attempt < max_retries:
            try:
                message = MIMEMultipart("related")
                message["From"] = sender_email
                message["To"] = receivers_email
                message["Subject"] = subject
                if cc:
                    message["Cc"] = cc
                if not attachments:
                    attachments = []

                message.attach(MIMEText(body, "html"))

                # Attach files
                for attachment in attachments:
                    with open(attachment, "rb") as file:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(file.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", f"attachment; filename= {attachment.split('/')[-1]}")
                    message.attach(part)

                all_recipients = [email.strip() for email in receivers_email.split(",")]
                if cc:
                    all_recipients += [email.strip() for email in cc.split(",")]

                with smtplib.SMTP(self.smtp_server, self.port) as server:
                    server.sendmail(sender_email, all_recipients, message.as_string())

                logging.info("Email sent successfully!")
                return  # Exit the function if successful

            except Exception as e:
                logging.error(
                    "ERROR Exception occurred while sending SMTP Mail Error: {}".format(str(e)), exc_info=True
                )
                attempt += 1
                if attempt < max_retries:
                    logging.info(f"Retrying... Attempt {attempt + 1} of {max_retries} in {retry_delay} seconds.")
                    time.sleep(retry_delay)
                else:
                    logging.error("Max retries reached. Failed to send email.")
                    raise Exception(f"Failed to send email after {max_retries} attempts: {str(e)}")