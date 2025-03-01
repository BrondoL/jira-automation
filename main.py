from flask import Flask, jsonify, render_template
from flask_cors import CORS

from config import Config
from controller import sheet_controller, ticket_controller
from pkg.jira import JiraClient
from repository import jira_repository, sheet_repository, teams_repository
from route import create_routes
from service import jira_service, sheet_service, teams_service

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}}, allow_headers=['Content-Type', 'X-Requested-With', 'Authorization'])

jira_client = JiraClient(
    base_url=Config.JIRA_URL,
    username=Config.JIRA_USER,
    token=Config.JIRA_API_TOKEN,
    project_key=Config.JIRA_PROJECT_KEY,
    issue_type=Config.JIRA_ISSUE_TYPE,
    team_id=Config.JIRA_TEAM_ID
)

google_sheet_repository = sheet_repository.GoogleSheetRepositoryRepository(Config.SHEET_CREDENTIAL_FILE, Config.SHEET_ID)
teams_repository = teams_repository.TeamsRepositoryRepository()
ticket_repository = jira_repository.JiraRepository(client=jira_client)

get_all_responses_service = sheet_service.GetAllGoogleSheetResponsesService(google_sheet_repository)
delete_all_responses_service = sheet_service.DeleteAllGoogleSheetResponsesService(google_sheet_repository)
send_message_to_team_service = teams_service.SendTeamsMessageService(teams_repository)
ticket_service = jira_service.JiraService(ticket_repository)

google_sheet_controller = sheet_controller.GoogleSheetController(
        get_all_responses_service,
        delete_all_responses_service,
        send_message_to_team_service
    )
tickets_controller = ticket_controller.TicketController(
    send_message_to_team_service,
    ticket_service
)

api, web = create_routes(
    google_sheet_controller,
    tickets_controller
)
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(web)

@app.errorhandler(404)
def not_found_error(error):
    app.logger.error(f"error: {error}")
    return jsonify({"message": "The requested resource was not found."}), 404
@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error(f"error: {error}")
    return jsonify({"message": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)