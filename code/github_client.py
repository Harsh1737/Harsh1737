#!/usr/bin/env python3
"""
Client for interacting with the GitHub API.
"""

import json
import logging
from urllib.request import Request, urlopen
from urllib.error import URLError

logger = logging.getLogger(__name__)

class GitHubClient:
    """A client for interacting with the GitHub API."""
    API_BASE_URL = "https://api.github.com"

    def __init__(self, username, token=None):
        """
        Initialize the GitHub client.
        Args:
            username (str): The GitHub username.
            token (str, optional): A GitHub PAT for authentication. Defaults to None.
        """
        self.username = username
        self.token = token
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    def get_user_repos(self):
        """Fetch all public repositories for the configured user."""
        url = f"{self.API_BASE_URL}/users/{self.username}/repos?per_page=100&sort=updated&type=owner"
        logger.info(f"Fetching repositories from {url}")
        
        req = Request(url, headers=self.headers)
        
        try:
            with urlopen(req, timeout=10) as response:
                if self.token:
                    logger.info("Authenticated request successful.")
                return json.loads(response.read().decode('utf-8'))
        except URLError as e:
            logger.error(f"Error fetching repos: {e}")
            return []
