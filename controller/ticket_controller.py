import logging

from flask import jsonify, render_template

from config import Config
from model import sheet
from service import jira_service, teams_service, notif_service
from util import delete_response, get_responses, save_result, get_result, get_results

class TicketController:
    def __init__(
        self,
        send_message_to_team_service: teams_service.SendTeamsMessageService,
        ticket_service: jira_service.JiraService,
        notif_service: notif_service.NotifService
    ):
        self.send_message_to_team_service = send_message_to_team_service
        self.jira_service = ticket_service
        self.notif_service = notif_service

    def accept(self, id):
        try:
            responses = get_responses()
            data = None

            # Mencari data dari google sheet responses
            for response in responses:
                if response["__PowerAppsId__"] == id:
                    data = response
                    break

            logging.info(f"Data: {data}")
            # Jika tidak ada, maka akan mencari data dari hasil yang sudah disimpan
            if not data:
                result = get_result(id)
                # Jika tidak ketemu, maka render not found
                if not result:
                    return render_template('not_found.html')
                else:
                    # Jika ada, namun belum pernah dibuatkan tiket jira
                    if not result["key"]:
                        return render_template('not_found.html')

                    # Jika ada, dan sudah dibuatkan tiket jira, maka render accept.html
                    jira_url = Config.JIRA_URL + "/browse/" + result["key"]
                    return render_template('accept.html', data=result, jira_url=jira_url)

            response = self.jira_service.create_issue(data)
            jira_url = Config.JIRA_URL + "/browse/" + response["key"]

            save_result(data, response["key"])
            delete_response(id)

            self.send_message_to_team_service.send_message_for_accept(data, response["key"])

            customer = data["Reporter"].split("@")[0]
            ticket = {
                "id": response["key"],
                "title": data["Summary"],
                "assignee": data["Assignee"],
                "priority": data["Priority"],
                "customer": customer
            }
            self.notif_service.accept_notification(ticket, data["Reporter"])

            return render_template('accept.html', data=data, jira_url=jira_url)
        except Exception as e:
            logging.error(f"error: {e}", exc_info=True)
            return jsonify({"message": "Internal Server Error"}), 500

    def reject(self, id):
        try:
            # Delete response from responses.json, and return the data
            response = delete_response(id)
            logging.info(f"Response: {response}")
            # jika tidak ada data
            if not response:
                # ambil dari results.json
                result = get_result(id)
                # jika tidak ada juga, maka render not found
                if not result:
                    return render_template('not_found.html')
                else:
                    # jika ada, namun belum pernah dibuatkan tiket jira, maka render not found
                    if result["key"]:
                        return render_template('not_found.html')

                    # Jika ada, maka render reject.html
                    return render_template('reject.html', response=result)

            # Jika ada response, maka simpan hasilnya ke results.json
            save_result(response)

            self.send_message_to_team_service.send_message_for_reject(response)

            customer = response["Reporter"].split("@")[0]
            ticket = {
                "title": response["Summary"],
                "assignee": response["Assignee"],
                "priority": response["Priority"],
                "customer": customer
            }
            self.notif_service.reject_notification(ticket, response["Reporter"])

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

    def check_status(self):
        try:
            # Get data dari results.json
            results = get_results()
            # filter data yang statusnya belum "Done" dan keynya tidak None
            data = [result for result in results.values() if result.get("status", None) != "Done" and result.get("key") != None]
            tickets = []

            for ticket in data:
                # Check status sekarang di jira, jika statusnya berubah, maka akan diupdate statusnya di resuls.json
                status_before = ticket.get("status", None)
                status = self.jira_service.check_status(ticket.get("key"), ticket.get("status", None))

                reporter = ticket["Reporter"]
                customer = ticket["Reporter"].split("@")[0]
                ticket = {
                    "id": ticket["key"],
                    "title": ticket["Summary"],
                    "assignee": ticket["Assignee"],
                    "priority": ticket["Priority"],
                    "customer": customer,
                    "status_before" : status_before,
                    "current_status" : status
                }

                if status == "In Progress":
                    self.notif_service.in_progress_notification(ticket, reporter)
                elif status == "Done":
                    self.notif_service.done_notification(ticket, reporter)

                tickets.append(ticket)

            return jsonify(ticket)
        except Exception as e:
            logging.error(f"error: {e}", exc_info=True)
            return jsonify({"message": "Internal Server Error"}), 500