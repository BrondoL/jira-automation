import requests

from config import Config


class TeamsRepositoryRepository():
    def __init__(self):
        self.webhook_url = Config.WEBHOOK_URL
        self.base_url = Config.BASE_URL
        self.jira_url = Config.JIRA_URL

    def send_message_for_new_ticket(self, user, data) -> bool:
        payload = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "contentUrl": None,
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.5",
                        "body": [
                            {
                                "type": "ColumnSet",
                                "columns": [
                                    {
                                        "type": "Column",
                                        "items": [
                                            {
                                                "type": "Image",
                                                "style": "person",
                                                "url": user["avatar"],
                                                "altText": user["name"],
                                                "size": "small"
                                            }
                                        ],
                                        "width": "auto"
                                    },
                                    {
                                        "type": "Column",
                                        "items": [
                                            {
                                                "type": "TextBlock",
                                                "size": "medium",
                                                "weight": "bolder",
                                                "text": f"Hi <at>{user['name']}</at>",
                                                "wrap": True
                                            },
                                            {
                                                "type": "TextBlock",
                                                "spacing": "None",
                                                "text": "A New Ticket Has Been Created",
                                                "isSubtle": True,
                                                "wrap": True
                                            }
                                        ],
                                        "width": "stretch"
                                    }
                                ]
                            },
                            {
                                "type": "ColumnSet",
                                "columns": [
                                    {
                                        "type": "Column",
                                        "items": [
                                            {
                                                "type": "TextBlock",
                                                "weight": "Bolder",
                                                "text": data["Summary"],
                                                "color": "Accent",
                                                "style": "default",
                                                "fontType": "Default",
                                                "size": "Large",
                                                "wrap": True
                                            }
                                        ],
                                        "width": "stretch"
                                    }
                                ]
                            },
                            {
                                "type": "FactSet",
                                "facts": [
                                    {
                                        "title": "Requestor:",
                                        "value": data["Reporter"]
                                    },
                                    {
                                        "title": "Priority:",
                                        "value": data["Priority"]
                                    },
                                    {
                                        "title": "Task Level:",
                                        "value": data["Level"]
                                    }
                                ]
                            },
                            {
                                "type": "TextBlock",
                                "text": data["Description"],
                                "wrap": True
                            },
                            {
                                "type": "TextBlock",
                                "text": "⚠️ Only the ticket owner can take actions on this ticket. If you believe this is a mistake, please contact the ticket owner or an administrator for further assistance.",
                                "wrap": True,
                                "fontType": "Monospace",
                                "spacing": "ExtraLarge",
                                "size": "Small"
                            }
                        ],
                        "actions": [
                            {
                                "type": "Action.OpenUrl",
                                "title": "Accept",
                                "url": self.base_url + "/tickets/accept/" + data["__PowerAppsId__"],
                                "iconUrl": "https://cdn-icons-png.flaticon.com/512/4315/4315445.png"
                            },
                            {
                                "type": "Action.OpenUrl",
                                "title": "Reject",
                                "url": self.base_url + "/tickets/reject/" + data["__PowerAppsId__"],
                                "iconUrl": "https://cdn-icons-png.freepik.com/512/11695/11695709.png"
                            }
                        ],
                        "msteams": {
                            "entities": [
                                {
                                    "type": "mention",
                                    "text": f"<at>{user['name']}</at>",
                                    "mentioned": {
                                        "id": user["email"],
                                        "name": user["name"]
                                    }
                                }
                            ]
                        }
                    }
                }
            ]
        }

        response = requests.post(
            self.webhook_url,
            json=payload
        )

        return response.status_code == 202

    def send_message_for_morning_update(self, in_progress, done):
        payload = {
            "type": "message",
            "attachments": [
                {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "contentUrl": None,
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.5",
                    "body": [
                    {
                        "type": "TextBlock",
                        "text": "✨Daily Jira Ticket Status✨",
                        "size": "Large",
                        "wrap": True,
                        "style": "heading",
                        "horizontalAlignment": "Center",
                        "color": "Accent"
                    },
                    {
                        "type": "ColumnSet",
                        "columns": [
                        {
                            "type": "Column",
                            "width": "auto",
                            "items": [
                            {
                                "type": "TextBlock",
                                "size": "Medium",
                                "weight": "Bolder",
                                "text": "- **Unresolved Jira Tickets**"
                            },
                            {
                                "type": "TextBlock",
                                "text": "The following tickets are still pending and not marked as Done:",
                                "wrap": True
                            },
                            {
                                "type": "TextBlock",
                                "text": in_progress,
                                "wrap": True
                            }
                            ]
                        }
                        ]
                    },
                    {
                        "type": "ColumnSet",
                        "columns": [
                        {
                            "type": "Column",
                            "width": "auto",
                            "items": [
                            {
                                "type": "TextBlock",
                                "size": "Medium",
                                "weight": "Bolder",
                                "text": "- **Rankings for This Month**"
                            },
                            {
                                "type": "TextBlock",
                                "text": "Here is the current ranking based on story points for this month:",
                                "wrap": True
                            },
                            {
                                "type": "TextBlock",
                                "text": done,
                                "wrap": True
                            }
                            ]
                        }
                        ]
                    },
                    {
                        "type": "TextBlock",
                        "text": "Let's keep up the good work and strive for more progress today! 🔥",
                        "wrap": True,
                        "color": "Warning"
                    }
                    ],
                    "actions": [
                    {
                        "type": "Action.OpenUrl",
                        "title": "View Board",
                        "url": "https://altoid.atlassian.net/jira/software/c/projects/DAS/boards/397"
                    }
                    ]
                }
                }
            ]
        }

        response = requests.post(
            self.webhook_url,
            json=payload
        )

        return response.status_code == 202

    def send_message_for_evening_update(self, today, not_ack):
        payload = {
            "type": "message",
            "attachments": [
                {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "contentUrl": None,
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.5",
                    "body": [
                    {
                        "type": "TextBlock",
                        "text": "✨Today's Ticket Recap✨",
                        "size": "Large",
                        "wrap": True,
                        "style": "heading",
                        "horizontalAlignment": "Center",
                                    "color": "Accent"
                    },
                    {
                        "type": "ColumnSet",
                        "columns": [
                        {
                            "type": "Column",
                            "width": "auto",
                            "items": [
                            {
                                "type": "TextBlock",
                                "text": "Newly Created Tickets:",
                                "weight": "Bolder"
                            },
                            {
                                "type": "TextBlock",
                                "text": today,
                                "wrap": True
                            }
                            ]
                        }
                        ]
                    },
                    {
                        "type": "ColumnSet",
                        "columns": [
                        {
                            "type": "Column",
                            "width": "auto",
                            "items": [
                            {
                                "type": "TextBlock",
                                "text": "Unacknowledged Tickets:",
                                "weight": "Bolder"
                            },
                            {
                                "type": "TextBlock",
                                "text": not_ack,
                                "wrap": True
                            }
                            ]
                        }
                        ]
                    },
                    {
                        "type": "TextBlock",
                        "text": "Great work today, everyone! Enjoy the rest of your evening! 🌆",
                        "wrap": True,
                        "color": "Warning"
                    }
                    ]
                }
                }
            ]
        }

        response = requests.post(
            self.webhook_url,
            json=payload
        )

        return response.status_code == 202

    def send_message_for_reject(self, user, data):
        payload = {
            "type": "message",
            "attachments": [
                {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "contentUrl": None,
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.5",
                    "body": [
                    {
                        "type": "ColumnSet",
                        "columns": [
                        {
                            "type": "Column",
                            "items": [
                            {
                                "type": "Image",
                                "style": "person",
                                "url": user["avatar"],
                                "altText": user["name"],
                                "size": "small"
                            }
                            ],
                            "width": "auto"
                        },
                        {
                            "type": "Column",
                            "items": [
                            {
                                "type": "TextBlock",
                                "size": "medium",
                                "weight": "bolder",
                                "text": f"Hi <at>{user['name']}</at>",
                                "wrap": True
                            },
                            {
                                "type": "TextBlock",
                                "spacing": "None",
                                "text": "A Ticket Has Been Acknowledge",
                                "isSubtle": True,
                                "wrap": True
                            }
                            ],
                            "width": "stretch"
                        }
                        ]
                    },
                    {
                        "type": "ColumnSet",
                        "columns": [
                        {
                            "type": "Column",
                            "items": [
                            {
                                "type": "TextBlock",
                                "weight": "Bolder",
                                "text": "❌ The Ticket Has Been Rejected. ❌",
                                "color": "Attention",
                                "style": "default",
                                "fontType": "Default",
                                "size": "Large",
                                "wrap": True
                            }
                            ],
                            "width": "stretch"
                        }
                        ]
                    },
                    {
                        "type": "FactSet",
                        "facts": [
                        {
                            "title": "Summary:",
                            "value": data["Summary"]
                        },
                        {
                            "title": "Assignee:",
                            "value": data["Assignee"]
                        },
                        {
                            "title": "Requestor:",
                            "value": data["Reporter"]
                        },
                        {
                            "title": "Priority:",
                            "value": data["Priority"]
                        }
                        ]
                    }
                    ],
                    "msteams": {
                    "entities": [
                        {
                            "type": "mention",
                            "text": f"<at>{user['name']}</at>",
                            "mentioned": {
                                "id": user["email"],
                                "name": user["name"]
                            }
                        }
                    ]
                    }
                }
                }
            ]
        }

        response = requests.post(
            self.webhook_url,
            json=payload
        )

        return response.status_code == 202

    def send_message_for_accept(self, user, data, ticket_key):
        payload = {
            "type": "message",
            "attachments": [
                {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "contentUrl": None,
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.5",
                    "body": [
                    {
                        "type": "ColumnSet",
                        "columns": [
                        {
                            "type": "Column",
                            "items": [
                            {
                                "type": "Image",
                                "style": "person",
                                "url": user["avatar"],
                                "altText": user["name"],
                                "size": "small"
                            }
                            ],
                            "width": "auto"
                        },
                        {
                            "type": "Column",
                            "items": [
                            {
                                "type": "TextBlock",
                                "size": "medium",
                                "weight": "bolder",
                                "text": f"Hi <at>{user['name']}</at>",
                                "wrap": True
                            },
                            {
                                "type": "TextBlock",
                                "spacing": "None",
                                "text": "A Ticket Has Been Acknowledge",
                                "isSubtle": True,
                                "wrap": True
                            }
                            ],
                            "width": "stretch"
                        }
                        ]
                    },
                    {
                        "type": "ColumnSet",
                        "columns": [
                        {
                            "type": "Column",
                            "items": [
                            {
                                "type": "TextBlock",
                                "weight": "Bolder",
                                "text": "✅ The Ticket Has Been Successfully Created. ✅",
                                "color": "Good",
                                "style": "default",
                                "fontType": "Default",
                                "size": "Large",
                                "wrap": True
                            }
                            ],
                            "width": "stretch"
                        }
                        ]
                    },
                    {
                        "type": "FactSet",
                        "facts": [
                        {
                            "title": "Number:",
                            "value": "DAS-9821"
                        },
                        {
                            "title": "Summary:",
                            "value": data["Summary"]
                        },
                        {
                            "title": "Assignee:",
                            "value": data["Assignee"]
                        },
                        {
                            "title": "Requestor:",
                            "value": data["Reporter"]
                        },
                        {
                            "title": "Priority:",
                            "value": data["Priority"]
                        }
                        ]
                    }
                    ],
                    "actions": [
                    {
                        "type": "Action.OpenUrl",
                        "title": "View Ticket",
                        "url": f"{self.jira_url}/browse/{ticket_key}"
                    }
                    ],
                    "msteams": {
                    "entities": [
                        {
                            "type": "mention",
                            "text": f"<at>{user['name']}</at>",
                            "mentioned": {
                                "id": user["email"],
                                "name": user["name"]
                            }
                        }
                    ]
                    }
                }
                }
            ]
        }

        response = requests.post(
            self.webhook_url,
            json=payload
        )

        return response.status_code == 202

    def send_message_for_incomplete(self, tickets):
        payload = {
            "type": "message",
            "attachments": [
                {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "contentUrl": None,
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.5",
                    "body": [
                    {
                        "type": "TextBlock",
                        "text": "⚠️ **Incomplete Jira Tickets Notification** ⚠️",
                        "size": "Large",
                        "wrap": True,
                        "style": "heading",
                        "horizontalAlignment": "Center",
                        "color": "Attention"
                    },
                    {
                        "type": "ColumnSet",
                        "columns": [
                        {
                            "type": "Column",
                            "width": "auto",
                            "items": [
                            {
                                "type": "TextBlock",
                                "size": "Medium",
                                "weight": "Bolder",
                                "text": "**Jira Tickets with Missing Fields**"
                            },
                            {
                                "type": "TextBlock",
                                "text": "The following Jira tickets are missing important fields. Please review and update them accordingly:",
                                "wrap": True
                            },
                            {
                                "type": "TextBlock",
                                "text": tickets,
                                "wrap": True
                            }
                            ]
                        }
                        ]
                    },
                    {
                        "type": "TextBlock",
                        "text": "Please make sure all required fields are completed to ensure smooth tracking of Jira tickets. Thank you for your cooperation! 😊",
                        "wrap": True
                    }
                    ]
                }
                }
            ]
        }

        response = requests.post(
            self.webhook_url,
            json=payload
        )

        return response.status_code == 202