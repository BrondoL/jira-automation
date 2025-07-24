import logging

from flask import current_app, jsonify

from service import sheet_service, teams_service


class GoogleSheetController:
    def __init__(
        self,
        get_all_responses_service: sheet_service.GetAllGoogleSheetResponsesService,
        delete_all_responses_service: sheet_service.DeleteAllGoogleSheetResponsesService,
        send_message_to_team_service: teams_service.SendTeamsMessageService
    ):
        self.get_all_responses_service = get_all_responses_service
        self.delete_all_responses_service = delete_all_responses_service
        self.send_message_to_team_service = send_message_to_team_service

    def get_all_responses(self):
        try:
            responses = self.get_all_responses_service.execute()
            if not len(responses):
                return jsonify({"message": "no response found in google sheets"}), 404

            for response in responses:
                self.send_message_to_team_service.send_message_for_new_ticket(response)

            ok = self.delete_all_responses_service.execute()
            if not ok:
                current_app.logger.error("Error when deleting the responses.")
                return jsonify({"message": "Internal Server Error"}), 500

            return jsonify(responses)
        except Exception as e:
            logging.error(f"error: {e}", exc_info=True)
            return jsonify({"message": "Internal Server Error"}), 500