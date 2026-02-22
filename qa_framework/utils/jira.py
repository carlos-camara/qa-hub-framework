import os
import json
import base64
import requests
from ..core.config_manager import ConfigManager
from .logger import ContextualLogger

class JiraConnector:
    """
    Utility to interact with Jira Cloud REST API.
    Supports posting comments, uploading attachments, and updating issue details.
    """

    def __init__(self):
        self.config = ConfigManager.instance()
        self.url = self.config.get('Jira.url', os.getenv('JIRA_URL'))
        self.user = self.config.get('Jira.user_email', os.getenv('JIRA_USER_EMAIL'))
        self.token = self.config.get('Jira.api_token', os.getenv('JIRA_API_TOKEN'))
        
        if self.url:
            self.url = self.url.rstrip('/')
            
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Basic {self._get_auth_string()}"
        }

    def _get_auth_string(self):
        """Generates the Basic Auth string for Jira Cloud."""
        if not self.user or not self.token:
            return ""
        auth_str = f"{self.user}:{self.token}"
        return base64.b64encode(auth_str.encode()).decode()

    def is_configured(self):
        """Checks if all required Jira credentials are present."""
        return all([self.url, self.user, self.token])

    def add_comment(self, issue_key, comment_text):
        """
        Adds a comment to a Jira issue.
        """
        if not self.is_configured():
            ContextualLogger.warning("Jira not configured. Skipping comment.")
            return False

        endpoint = f"{self.url}/rest/api/3/issue/{issue_key}/comment"
        
        # Jira Cloud uses ADf (Atlassian Document Format) for API v3
        payload = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "text": comment_text,
                                "type": "text"
                            }
                        ]
                    }
                ]
            }
        }

        try:
            response = requests.post(
                endpoint,
                data=json.dumps(payload),
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 201:
                ContextualLogger.debug(f"Comment added to {issue_key}")
                return True
            else:
                ContextualLogger.error(f"Failed to add comment to {issue_key}: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            ContextualLogger.error(f"Error connecting to Jira: {str(e)}")
            return False

    def upload_attachment(self, issue_key, file_path):
        """
        Uploads a file as an attachment to a Jira issue.
        """
        if not self.is_configured():
            return False

        if not os.path.exists(file_path):
            ContextualLogger.error(f"File not found: {file_path}")
            return False

        endpoint = f"{self.url}/rest/api/3/issue/{issue_key}/attachments"
        headers = self.headers.copy()
        del headers["Content-Type"] # Requests will set multipart/form-data
        headers["X-Atlassian-Token"] = "no-check"

        try:
            with open(file_path, "rb") as f:
                files = {"file": f}
                response = requests.post(
                    endpoint,
                    files=files,
                    headers=headers,
                    timeout=20
                )
                
            if response.status_code == 200:
                ContextualLogger.debug(f"Attachment uploaded to {issue_key}")
                return True
            else:
                ContextualLogger.error(f"Failed to upload attachment to {issue_key}: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            ContextualLogger.error(f"Error uploading to Jira: {str(e)}")
            return False

    def update_description(self, issue_key, description_text):
        """
        Updates the Jira issue description with Gherkin scenario text.
        """
        if not self.is_configured():
            return False

        endpoint = f"{self.url}/rest/api/3/issue/{issue_key}"
        
        payload = {
            "fields": {
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "codeBlock",
                            "attrs": {"language": "gherkin"},
                            "content": [{"type": "text", "text": description_text}]
                        }
                    ]
                }
            }
        }

        try:
            response = requests.put(
                endpoint,
                data=json.dumps(payload),
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 204
        except Exception as e:
            ContextualLogger.error(f"Error updating description in Jira: {str(e)}")
            return False
