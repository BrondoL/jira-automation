import logging

from flask import current_app, jsonify, request
from service.form_service import FormService
from service.teams_service import SendTeamsMessageService
from model.form import FormSchema
from marshmallow import ValidationError
from werkzeug.exceptions import UnsupportedMediaType, BadRequest
from model.sheet import GoogleSheetResponse

class FormController:
    def __init__(
        self,
        form_service: FormService,
        team_service: SendTeamsMessageService
    ):
        self.form_service = form_service
        self.team_service = team_service

    def store(self):
        try:
            json_data = request.get_json()
            if not json_data:
                return jsonify({"message": "No input data provided"}), 400

            form_schema = FormSchema()
            data = form_schema.load(json_data)

            form = self.form_service.save_response(data)
            response = GoogleSheetResponse(id=1, data=form)
            self.team_service.send_message_for_new_ticket(response)

            return jsonify(form), 201
        except Exception as e:
            logging.error(f"error: {e}", exc_info=True)

            if isinstance(e, ValidationError):
                return jsonify({"message": "Validation failed", "errors": e.messages}), 422
            elif isinstance(e, UnsupportedMediaType):
                return jsonify({"message": "Content-Type must be application/json"}), 415
            elif isinstance(e, BadRequest):
                return jsonify({"message": "Bad Request"}), 400

            return jsonify({"message": "Internal Server Error"}), 500