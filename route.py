from flask import Blueprint, jsonify, request

from config import Config
from controller import sheet_controller, ticket_controller


def create_routes(
    sheet_controller: sheet_controller.GoogleSheetController,
    ticket_controller: ticket_controller.TicketController
):
    api = Blueprint('api', __name__)

    @api.before_request
    def check_token():
        token = request.args.get('token')
        expected_token = Config.SECRET_TOKEN

        # If 'token' is in the query params and it doesn't match the expected token
        if token != expected_token:
            return jsonify({'error': 'Unauthorized'}), 401

    api.route('/google-sheet/responses', methods=['GET'])(sheet_controller.get_all_responses)
    api.route('/tickets/morning', methods=['GET'])(ticket_controller.morning)
    api.route('/tickets/evening', methods=['GET'])(ticket_controller.evening)
    api.route('/tickets/resend', methods=["GET"])(ticket_controller.resend)
    api.route('/tickets/incomplete', methods=["GET"])(ticket_controller.incomplete)

    # ================================

    web = Blueprint('web', __name__)

    web.route('/tickets/reject/<id>', methods=['GET'])(ticket_controller.reject)
    web.route('/tickets/accept/<id>', methods=['GET'])(ticket_controller.accept)

    return api, web