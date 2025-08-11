import logging
from pkg import smtp
from string import Template
from config import Config

class NotifService:
    def __init__(self, smtp_client: smtp.SMTPClient):
        self.smtp_client = smtp_client
        self.jira_url = Config.JIRA_URL
        self.sender_email = Config.EMAIL_FROM
        self.cc_email = Config.EMAIL_CC

    def accept_notification(self, ticket, email: str):
        try:
            html = Template("""\
                <!DOCTYPE html>
                <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <h2 style="color: #4CAF50;">[Ticket #$ticket_id] Request Accepted</h2>
                    <p>Dear $customer_name,</p>

                    <p>Your request has been <strong>accepted</strong>. Our team will begin processing it soon.</p>

                    <ul>
                    <li><strong>Title:</strong> $ticket_title</li>
                    <li><strong>Assignee:</strong> $ticket_assignee</li>
                    <li><strong>Priority:</strong> $ticket_priority</li>
                    <li><strong>Status:</strong> Accepted</li>
                    </ul>

                    <p>
                    <a href="$jira_url/browse/$ticket_id"
                        style="display: inline-block; padding: 3px 8px; background-color: #1976D2; color: #fff; text-decoration: none; border-radius: 5px;">
                        View Ticket
                    </a>
                    </p>

                    <p>Thank you,<br>SRE Core</p>
                </body>
                </html>
            """)

            body = html.substitute(
                ticket_id=ticket.get("id"),
                ticket_title=ticket.get("title"),
                ticket_assignee=ticket.get("assignee"),
                ticket_priority=ticket.get("priority"),
                customer_name=ticket.get("customer"),
                jira_url=self.jira_url
            )

            self.smtp_client.send_email(
                subject=f"[Ticket #{ticket.get('id')}] Request Accepted",
                sender_email=self.sender_email,
                receivers_email=email,
                cc=self.cc_email,
                body=body,
            )

            logging.info(f"Notif accept sent successfully to {email}")
        except Exception as e:
            logging.error(f"Failed to send notif accept to {email}: {e}")

    def reject_notification(self, ticket, email: str):
        try:
            rejection_reason_html = ""
            if ticket.get("rejection_reason"):
                rejection_reason_html = f"<li><strong>Rejection Reason:</strong> {ticket.get('rejection_reason')}</li>"

            html = Template("""\
                <!DOCTYPE html>
                <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <h2 style="color: #F44336;">[Ticket #] Request Rejected</h2>
                    <p>Dear $customer_name,</p>

                    <p>Your request has been <strong>rejected</strong>.</p>

                    <ul>
                    <li><strong>Title:</strong> $ticket_title</li>
                    <li><strong>Assignee:</strong> $ticket_assignee</li>
                    <li><strong>Priority:</strong> $ticket_priority</li>
                    <li><strong>Status:</strong> Rejected</li>
                    $rejection_reason_html
                    </ul>

                    <p>Thank you,<br>SRE Core</p>
                </body>
                </html>
            """)

            body = html.substitute(
                ticket_title=ticket.get("title"),
                ticket_assignee=ticket.get("assignee"),
                ticket_priority=ticket.get("priority"),
                customer_name=ticket.get("customer"),
                rejection_reason_html=rejection_reason_html,
                jira_url=self.jira_url
            )

            self.smtp_client.send_email(
                subject="[Ticket #] Request Rejected",
                sender_email=self.sender_email,
                receivers_email=email,
                cc=self.cc_email,
                body=body,
            )

            logging.info(f"Notif reject sent successfully to {email}")
        except Exception as e:
            logging.error(f"Failed to send notif reject to {email}: {e}")

    def in_progress_notification(self, ticket, email: str):
        try:
            html = Template("""\
                <!DOCTYPE html>
                <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <h2 style="color: #FF9800;">[Ticket #$ticket_id] Request In Progress</h2>
                    <p>Dear $customer_name,</p>

                    <p>Your request is currently being <strong>worked on</strong>.</p>

                    <ul>
                    <li><strong>Title:</strong> $ticket_title</li>
                    <li><strong>Assignee:</strong> $ticket_assignee</li>
                    <li><strong>Priority:</strong> $ticket_priority</li>
                    <li><strong>Status:</strong> In Progress</li>
                    </ul>

                    <p>
                    <a href="$jira_url/browse/$ticket_id"
                        style="display: inline-block; padding: 3px 8px; background-color: #1976D2; color: #fff; text-decoration: none; border-radius: 5px;">
                        View Ticket
                    </a>
                    </p>

                    <p>We’ll notify you once it’s completed.</p>

                    <p>Thank you,<br>SRE Core</p>
                </body>
                </html>
            """)

            body = html.substitute(
                ticket_id=ticket.get("id"),
                ticket_title=ticket.get("title"),
                ticket_assignee=ticket.get("assignee"),
                ticket_priority=ticket.get("priority"),
                customer_name=ticket.get("customer"),
                jira_url=self.jira_url
            )

            self.smtp_client.send_email(
                subject=f"[Ticket #{ticket.get('id')}] Request In Progress",
                sender_email=self.sender_email,
                receivers_email=email,
                cc=self.cc_email,
                body=body,
            )

            logging.info(f"Notif in progress sent successfully to {email}")
        except Exception as e:
            logging.error(f"Failed to send notif in progress to {email}: {e}")

    def done_notification(self, ticket, email: str):
        try:
            html = Template("""\
                <!DOCTYPE html>
                <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <h2 style="color: #4CAF50;">[Ticket #$ticket_id] Request Completed</h2>
                    <p>Dear $customer_name,</p>

                    <p>Your request has been <strong>successfully completed</strong>.</p>

                    <ul>
                    <li><strong>Title:</strong> $ticket_title</li>
                    <li><strong>Assignee:</strong> $ticket_assignee</li>
                    <li><strong>Priority:</strong> $ticket_priority</li>
                    <li><strong>Status:</strong> Completed</li>
                    </ul>

                    <p>
                    <a href="$jira_url/browse/$ticket_id"
                        style="display: inline-block; padding: 3px 8px; background-color: #1976D2; color: #fff; text-decoration: none; border-radius: 5px;">
                        View Ticket
                    </a>
                    </p>

                    <p style="margin: 0">If you have any questions, please reach out to us.</p>
                    <p style="font-size: 0.9em; color: #777;margin: 0">
                        P.S. If you feel this helped make your day easier, feel free to buy us a coffee ☕ :)
                    </p>

                    <p>Kind regards,<br>SRE Core</p>
                </body>
                </html>
            """)

            body = html.substitute(
                ticket_id=ticket.get("id"),
                ticket_title=ticket.get("title"),
                ticket_assignee=ticket.get("assignee"),
                ticket_priority=ticket.get("priority"),
                customer_name=ticket.get("customer"),
                jira_url=self.jira_url
            )

            self.smtp_client.send_email(
                subject=f"[Ticket #{ticket.get('id')}] Request Completed",
                sender_email=self.sender_email,
                receivers_email=email,
                cc=self.cc_email,
                body=body,
            )

            logging.info(f"Notif completed sent successfully to {email}")
        except Exception as e:
            logging.error(f"Failed to send notif completed to {email}: {e}")