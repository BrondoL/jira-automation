import json
from base64 import b64encode
from typing import Dict, List

import requests


class JiraClient:
    """
    A client to interact with Jira's REST API V3 for issue search functionality using Basic Authentication.
    """

    def __init__(self, base_url: str, username: str, token: str, project_key: str, issue_type: str, team_id : str):
        self.base_url = base_url
        self.username = username
        self.token = token
        self.project_key = project_key
        self.issue_type = issue_type
        self.team_id = team_id

        # Create Basic Auth header from username and token
        self.auth_header = self._create_basic_auth_header()

        # Search URL for Jira API
        self.search_url = f'{self.base_url}/rest/api/3/search/jql'
        self.create_url = f'{self.base_url}/rest/api/3/issue'
        self.search_user_url = f'{self.base_url}/rest/api/3/user/search'

    def _create_basic_auth_header(self) -> Dict:
        """
        Create Basic Auth header using the username and token.

        :return: Authorization header as a dictionary
        """
        credentials = f"{self.username}:{self.token}"
        encoded_credentials = b64encode(credentials.encode('utf-8')).decode('utf-8')
        return {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json',
        }

    def search_jira_issues(self, query, fields, max_results: int = 1) -> List[Dict]:
        """
        Search for Jira issues based on project, issue type, and date range (start of day to end of day).

        :param max_results: The maximum number of results to return (default: 1)
        :return: A list of issues that match the search criteria
        """
        jql_query = (
            f'project = "{self.project_key}" '
            f'AND issuetype = "{self.issue_type}" '
        )

        if query:
            jql_query += f"AND {query}"

        params = {
            'jql': jql_query,
            'fields': fields,
            'maxResults': max_results,
        }

        # Make the GET request with basic authentication header
        response = requests.get(self.search_url, headers=self.auth_header, params=params)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch issues: {response.text}")

        data = response.json()
        return data.get('issues', [])

    def create_issue(self, data, account_id, reporter_id):
        reporter = data["Reporter"]
        description = data["Description"] + f"\n\nReporter: {reporter}"
        priority = data["Priority"].split(" - ")[0]

        payload = json.dumps({
            "fields": {
                "project": {
                    "key": self.project_key
                },
                "issuetype": {
                    "name": self.issue_type
                },
                "parent": {
                    "key": "DAS-7286"
                },
				"customfield_10028": 2.0,
                "summary": data["Summary"],
                "description": {
                    "content": [
                        {
                            "content": [
                                {
                                    "text": description,
                                    "type": "text"
                                }
                            ],
                            "type": "paragraph"
                        }
                    ],
                    "type": "doc",
                    "version": 1
                },
                "priority": {
                    "name": priority
                },
                "assignee": {
                    "id": account_id
                },
                "reporter": {
                    "id": reporter_id
                },
                "customfield_10238": {
                    "value": "Easy"
                },
                "customfield_10001": self.team_id
            }
        })

        response = requests.post(
            url=self.create_url,
            headers=self.auth_header,
            data=payload
        )

        if response.status_code != 201:
            print(payload)
            raise Exception(f"Failed to create issue({response.status_code}): {response.text}")

        data = response.json()
        return data

    def search_user(self, email):
        params = {
            'query': email
        }

        # Make the GET request with basic authentication header
        response = requests.get(self.search_user_url, headers=self.auth_header, params=params)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch user: {response.text}")

        data = response.json()
        return data