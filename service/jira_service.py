import logging

from util import get_user, update_result_status, delete_result
from repository.jira_repository import JiraRepository


class JiraService:
    def __init__(self, repository: JiraRepository):
        self.repository = repository

    def get_tickets_in_progress(self):
        tickets = self.repository.find_tickets_in_progress()

        if not len(tickets):
            logging.warning("Jira Ticket (In Progress) is empty!")

        return tickets

    def get_tickets_done(self):
        tickets = self.repository.find_tickets_done_this_month()

        if not len(tickets):
            logging.warning("Jira Ticket (Done) is empty!")

        return tickets

    def get_tickets_today(self):
        tickets = self.repository.find_tickets_created_today()

        if not len(tickets):
            logging.warning("Jira Ticket (Today) is empty!")

        return tickets

    def get_incomplete_tickets(self):
        tickets = self.repository.find_incomplete_tickets()
        if not len(tickets):
            logging.warning("Jira Ticket (Incomplete) is empty!")

        return tickets

    def create_issue(self, data):
        user = get_user(data["Assignee"])
        if not user:
            raise Exception("Assignee not found in the database")

        account_id = user["id"]
        if not account_id:
            raise Exception("Assignee doesn't have an ID")
        reporter_id = account_id

        email = data["Reporter"]
        if email != user["email"]:
            reporter = self.repository.find_user(email)
            if not reporter:
                logging.warning("Reporter not found in Jira")
            else:
                reporter_id = reporter["accountId"]


        response = self.repository.create_issue(data, account_id, reporter_id)

        return response

    def check_status(self, key, status):
        ticket = self.repository.find_ticket_by_key(key)
        if not ticket:
            return None

        current_status = ticket["fields"]["status"]["name"]
        if status != current_status:
            update_result_status(key, current_status)

            if current_status == "In Progress":
                return current_status
            elif current_status == "Done":
                delete_result(key)
                return current_status

        return None