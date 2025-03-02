import logging
import os

from dotenv import load_dotenv

load_dotenv()

class Config:
  DEBUG = True
  HOST = os.getenv('HOST', '127.0.0.1')
  PORT = int(os.getenv('PORT', '8000'))
  BASE_URL = os.getenv('BASE_URL', 'http://127.0.0.1:8000')
  SECRET_TOKEN = os.getenv('SECRET_TOKEN', 'supersecret')

  WEBHOOK_URL = os.getenv('WEBHOOK_URL')
  JIRA_URL = os.getenv('JIRA_URL')
  JIRA_USER = os.getenv('JIRA_USER')
  JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')
  JIRA_PROJECT_KEY = os.getenv('JIRA_PROJECT_KEY')
  JIRA_ISSUE_TYPE = os.getenv('JIRA_ISSUE_TYPE')
  JIRA_TEAM_ID = os.getenv('JIRA_TEAM_ID')
  SHEET_ID = os.getenv('SHEET_ID')
  SHEET_CREDENTIAL_FILE = os.getenv('SHEET_CREDENTIAL_FILE')

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(asctime)s pid:%(process)s module:%(module)s %(message)s',
    datefmt='%d/%m/%y %H:%M:%S',
)