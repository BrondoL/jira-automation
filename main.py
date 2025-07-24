from flask import Flask, jsonify, request
from flask_cors import CORS

from config import Config
from controller import ticket_controller, form_controller
from pkg.jira import JiraClient
from pkg.smtp import SMTPClient
from repository import jira_repository, teams_repository, form_repository
from route import create_routes
from service import jira_service, teams_service, notif_service, form_service

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

smtp_client = SMTPClient(
    Config.SMTP_SERVER,
    Config.SMTP_PORT,
    Config.SMTP_USERNAME,
    Config.SMTP_PASSWORD
)

teams_repository = teams_repository.TeamsRepositoryRepository()
ticket_repository = jira_repository.JiraRepository(client=jira_client)
form_repository = form_repository.FormRepository()

send_message_to_team_service = teams_service.SendTeamsMessageService(teams_repository)
ticket_service = jira_service.JiraService(ticket_repository)
notif_service = notif_service.NotifService(smtp_client)
form_service = form_service.FormService(form_repository)

tickets_controller = ticket_controller.TicketController(
    send_message_to_team_service,
    ticket_service,
    notif_service
)

form_controller = form_controller.FormController(form_service, notif_service)

api, web = create_routes(
    tickets_controller,
    form_controller
)
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(web)

@app.after_request
def log_response_info(response):
    app.logger.info(f'"{request.method} {request.url}" | {response.status} | IP: {request.remote_addr}')
    return response

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