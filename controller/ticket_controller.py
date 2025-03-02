import logging

from flask import jsonify, render_template

from config import Config
from model import sheet
from service import jira_service, teams_service
from util import delete_response, get_responses


class TicketController:
    def __init__(
        self,
        send_message_to_team_service: teams_service.SendTeamsMessageService,
        ticket_service: jira_service.JiraService
    ):
        self.send_message_to_team_service = send_message_to_team_service
        self.jira_service = ticket_service

    def accept(self, id):
        try:
            responses = get_responses()
            data = None
            for response in responses:
                if response["__PowerAppsId__"] == id:
                    data = response
                    break

            logging.info(f"Data: {data}")
            if not data:
                return render_template('not_found.html')

            response = self.jira_service.create_issue(data)
            jira_url = Config.JIRA_URL + "/browse/" + response["key"]

            delete_response(id)

            self.send_message_to_team_service.send_message_for_accept(data, response["key"])

            return render_template('accept.html', data=data, jira_url=jira_url)
        except Exception as e:
            logging.error(f"error: {e}", exc_info=True)
            return jsonify({"message": "Internal Server Error"}), 500

    def reject(self, id):
        try:
            response = delete_response(id)
            logging.info(f"Response: {response}")
            if not response:
                return render_template('not_found.html')

            self.send_message_to_team_service.send_message_for_reject(response)

            return render_template('reject.html', response=response)
        except Exception as e:
            logging.error(f"error: {e}", exc_info=True)
            return jsonify({"message": "Internal Server Error"}), 500

    def morning(self):
        try:
            ticket_in_progress = self.jira_service.get_tickets_in_progress()
            ticket_done = self.jira_service.get_tickets_done()

            self.send_message_to_team_service.send_message_for_morning_update(ticket_in_progress, ticket_done)

            return jsonify({"in_progress": ticket_in_progress, "done": ticket_done})
        except Exception as e:
            logging.error(f"error: {e}", exc_info=True)
            return jsonify({"message": "Internal Server Error"}), 500

    def evening(self):
        try:
            ticket_today = self.jira_service.get_tickets_today()
            responses = get_responses()

            self.send_message_to_team_service.send_message_for_evening_update(ticket_today, responses)

            return jsonify({"today": ticket_today, "not_ack": responses})
        except Exception as e:
            logging.error(f"error: {e}", exc_info=True)
            return jsonify({"message": "Internal Server Error"}), 500

    def resend(self):
        try:
            responses = get_responses()
            responses = [
                sheet.GoogleSheetResponse(
                    id=str(i + 1),  # Using row number as ID
                    data=record
                ) for i, record in enumerate(responses)
            ]
            self.send_message_to_team_service.send_message_for_new_ticket(responses)

            return jsonify({"message": "ok"})
        except Exception as e:
            logging.error(f"error: {e}", exc_info=True)
            return jsonify({"message": "Internal Server Error"}), 500

    def incomplete(self):
        try:
            tickets = self.jira_service.get_incomplete_tickets()
            if not len(tickets):
                return jsonify({"message": "no incomplete tickets"})

            self.send_message_to_team_service.send_message_for_incomplete_ticket(tickets, Config.JIRA_URL)

            return jsonify(tickets)
        except Exception as e:
            logging.error(f"error: {e}", exc_info=True)
            return jsonify({"message": "Internal Server Error"}), 500