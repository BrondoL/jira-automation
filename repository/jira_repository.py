from pkg.jira import JiraClient

class JiraRepository():
    def __init__(self, client: JiraClient):
        self.jira_client = client

    def find_tickets_created_today(self):
        query = "created >= startOfDay() AND created <= endOfDay() order by assignee ASC, priority,status,customfield_10028 desc"
        field = "assignee,summary,priority"
        max_result = 100

        return self.jira_client.search_jira_issues(query, field, max_result)

    def find_tickets_in_progress(self):
        query = 'NOT status = "Done" order by assignee ASC, priority,status,customfield_10028 desc'
        field = "assignee,summary,priority,customfield_10028,status"
        max_result = 100

        return self.jira_client.search_jira_issues(query, field, max_result)

    def find_tickets_done_this_month(self):
        query = 'status = Done AND updated >= startOfMonth() AND updated <= endOfMonth() AND "Story Points" is not empty order by assignee asc'
        field = "assignee,customfield_10028"
        max_result = 1000

        return self.jira_client.search_jira_issues(query, field, max_result)

    def find_incomplete_tickets(self):
        query = '("Story Points" is empty or description is EMPTY or parent is EMPTY or assignee is EMPTY or "Team[Team]" is EMPTY) and (created >= startOfMonth() and created <= endOfMonth())'
        field = "assignee,summary"
        max_result = 100

        return self.jira_client.search_jira_issues(query, field, max_result)

    def create_issue(self, data, assignee_id, reporter_id):
        return self.jira_client.create_issue(data, assignee_id, reporter_id)

    def find_user(self, email):
        users = self.jira_client.search_user(email)
        if not len(users):
            return None

        return users[0]

    def find_ticket_by_key(self, key):
        query = f'key = "{key}"'
        field = "status,comment,attachment"

        tickets = self.jira_client.search_jira_issues(query, field)
        if not len(tickets):
            return None

        return tickets[0]