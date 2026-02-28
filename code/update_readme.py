#!/usr/bin/env python3
"""
GitHub Profile README Updater
Main entry point for the script.
"""

import logging
import os

from config import GITHUB_USERNAME
from github_client import GitHubClient
from core import build_repos_table, update_readme

# --- Logger Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def main():
    """Main execution."""
    github_token = os.getenv("README_PAT")
    if not github_token:
        logger.warning("No GITHUB_TOKEN found in environment. Proceeding with unauthenticated requests (rate limits may apply).")
    logger.debug(f"Fetching repositories for {GITHUB_USERNAME}...")
    client = GitHubClient(GITHUB_USERNAME, github_token)
    repos = client.get_user_repos()
    
    if not repos:
        logger.warning("No repositories found!")
        return
        
    logger.info(f"Found {len(repos)} repositories")
    repos_table = build_repos_table(repos)
    
    if update_readme(repos_table):
        logger.info("Done!")
    else:
        logger.error("Failed to update README")

if __name__ == "__main__":
    main()
