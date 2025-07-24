import logging
import time

from model import teams
from util import get_user, get_value


class SendTeamsMessageService:
    def __init__(self, repository):
        self.repository = repository

    def send_message_for_new_ticket(self, response) -> teams.TeamsMessageResponseDTO:
        data = response.data
        user = get_user(data["Assignee"])
        if not user:
            raise Exception("User not found!")

        ok = self.repository.send_message_for_new_ticket(user, data)
        if not ok:
            logging.warning(f"Error when notify this ticket: {data['__PowerAppsId__']}")

    def send_message_for_morning_update(self, in_progress, done):
        formatted_in_progress = ""
        for idx, ticket in enumerate(in_progress):
            username = get_value(ticket["fields"]["assignee"], "displayName")
            alias = "NaN"
            if username:
                user = get_user(username)
                if user:
                    alias = user["alias"]

            priority = get_value(ticket["fields"]["priority"], "name", "NaN")
            status = get_value(ticket["fields"]["status"], "name")
            summary = get_value(ticket["fields"], "summary")
            pts = get_value(ticket["fields"], "customfield_10028", "NaN")

            formatted_in_progress += f"{idx+1}. [{priority}] - {status} - {alias} - {summary} - {pts} pts\r"

        if formatted_in_progress == "":
            formatted_in_progress = "♻️ No tickets in backlog"

        users = {}
        tickets = {}
        formatted_done = ""
        for idx, ticket in enumerate(done):
            name = get_value(ticket["fields"]["assignee"], "displayName")
            if not name:
                continue

            pts = ticket["fields"]["customfield_10028"]

            if name in users:
                users[name] += pts
                tickets[name] += 1
            else:
                users[name] = pts
                tickets[name] = 1

        sorted_users_desc = dict(sorted(users.items(), key=lambda item: item[1], reverse=True))
        idx = 0
        for name, pts in sorted_users_desc.items():
            bold_name = name
            if idx < 3:
                bold_name = f"**{name}**"

            formatted_done += f"{idx+1}. {bold_name} - {tickets[name]} tickets - {pts} pts\r"
            idx += 1

        if formatted_done == "":
            formatted_done = "⚠️ No Tickets Completed This Month ⚠️"

        ok = self.repository.send_message_for_morning_update(formatted_in_progress, formatted_done)
        if not ok:
            logging.warning("Error when notify morning updates")

    def send_message_for_evening_update(self, today, not_ack):
        formatted_today = ""
        for idx, ticket in enumerate(today):
            username = get_value(ticket["fields"]["assignee"], "displayName")
            alias = "NaN"
            if username:
                user = get_user(username)
                if user:
                    alias = user["alias"]

            priority = get_value(ticket["fields"]["priority"], "name", "NaN")
            summary = get_value(ticket["fields"], "summary")

            formatted_today += f"{idx+1}. [{priority}] - {alias} - {summary}\r"

        if formatted_today == "":
            formatted_today = "♻️ No one made a ticket today"

        users = {}
        formatted_not_ack = ""
        for idx, ticket in enumerate(not_ack):
            username = ticket["Assignee"]
            user = get_user(username)
            alias = "NaN"
            if user:
                alias = user["alias"]
                if alias not in users:
                    users[alias] = {
                        "name": user["name"],
                        "email": user["email"],
                    }

            priority = ticket["Priority"]
            summary = ticket["Summary"]

            formatted_not_ack += f"{idx+1}. [{priority}] - {alias} - {summary}\r"

        if formatted_not_ack == "":
            formatted_not_ack = "♻️ All tickets have been acknowledged"

        ok = self.repository.send_message_for_evening_update(formatted_today, formatted_not_ack, users)
        if not ok:
            logging.warning(f"Error when notify evening updates")

    def send_message_for_reject(self, response):
        user = get_user(response["Assignee"])
        if not user:
            raise Exception("User not found!")

        ok = self.repository.send_message_for_reject(user, response)
        if not ok:
            logging.warning(f"Error when notify reject this ticket: {response['__PowerAppsId__']}")

    def send_message_for_accept(self, response, ticket_key):
        user = get_user(response["Assignee"])
        if not user:
            raise Exception("User not found!")

        ok = self.repository.send_message_for_accept(user, response, ticket_key)
        if not ok:
            logging.warning(f"Error when notify accept this ticket: {response['__PowerAppsId__']}")

    def send_message_for_incomplete_ticket(self, responses, jira_url):
        formatted_response = ""
        users = {}
        for idx, ticket in enumerate(responses):
            username = get_value(ticket["fields"]["assignee"], "displayName")
            alias = "NaN"
            if username:
                user = get_user(username)
                if user:
                    alias = user["alias"]
                    if alias not in users:
                        users[alias] = {
                            "name": user["name"],
                            "email": user["email"],
                        }

            summary = get_value(ticket["fields"], "summary")
            number = ticket["key"]
            link = f"{jira_url}/browse/{number}"

            formatted_response += f"{idx+1}. [{alias}] - [{summary}]({link})\r"

        ok = self.repository.send_message_for_incomplete(formatted_response, users)
        if not ok:
            logging.warning("Error when notify incomplete ticket")