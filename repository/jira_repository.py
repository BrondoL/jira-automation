class JiraRepository():
    def __init__(self, client):
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

    def create_issue(self, data, account_id):
        return self.jira_client.create_issue(data, account_id)