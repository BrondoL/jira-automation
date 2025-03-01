from dataclasses import dataclass
from typing import List, Optional


class JiraTicket:
    def __init__(self, key, summary, description, status, assignee=None):
        self.key = key
        self.summary = summary
        self.description = description
        self.status = status
        self.assignee = assignee

@dataclass
class CreateJiraTicketRequestDTO:
    summary: str
    description: str
    issue_type: str = "Task"

@dataclass
class JiraTicketResponseDTO:
    key: str
    summary: str
    description: str
    status: str
    assignee: Optional[str] = None

@dataclass
class JiraTicketsListResponseDTO:
    tickets: List[JiraTicketResponseDTO]