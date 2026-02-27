#!/usr/bin/env python3
"""
GitHub Profile README Updater
Automatically fetches repositories and updates the README with repo details.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError

# --- Configuration ---
GITHUB_USERNAME = "Harsh1737"
README_FILE = Path(__file__).parent.parent / "README.md"
REPO_START_MARKER = "<!-- START_REPOS -->"
REPO_END_MARKER = "<!-- END_REPOS -->"

# --- Logger Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def get_user_repos(username, token=None):
    """Fetch all public repositories for a GitHub user."""
    url = f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated&type=owner"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
        logger.info("Using provided GITHUB_TOKEN for authentication.")
    
    req = Request(url, headers=headers)
    
    try:
        with urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8'))
    except URLError as e:
        logger.error(f"Error fetching repos: {e}")
        return []

def get_emoji_for_repo():
    return "📦"

def format_language(language):
    """Format language name."""
    if not language:
        return "—"
    return f"`{language}`"

def build_repos_table(repos):
    """Build markdown table for repositories."""
    if not repos:
        return "No repositories found."
    
    # Filter out this repo itself and sort by stars then updated date
    repos = [r for r in repos if r["name"].lower() != "harsh1737"]
    repos = sorted(repos, key=lambda x: (-x["stargazers_count"], x["updated_at"]), reverse=True)
    
    table = "| &nbsp; | Repository | Description | Language | Stars |\n"
    table += "|--------|-----------|-------------|----------|-------|\n"
    
    for repo in repos:
        emoji = get_emoji_for_repo()
        name = repo["name"]
        url = repo["html_url"]
        description = (repo["description"] or "No description").strip()
        # Truncate long descriptions
        if len(description) > 40:
            description = description[:37] + "..."
        language = format_language(repo["language"])
        stars = repo["stargazers_count"]
        
        row = f"| {emoji} | [**{name}**]({url}) | {description} | {language} | ⭐ {stars} |\n"
        table += row
    
    return table

def update_readme(repos_table):
    """Update README file with repository table."""
    if not README_FILE.exists():
        logger.error(f"Error: {README_FILE} not found!")
        return False
    
    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Find the markers
    start_marker = REPO_START_MARKER
    end_marker = REPO_END_MARKER
    
    if start_marker not in content or end_marker not in content:
        logger.error("Error: Repository markers not found in README!")
        return False
    
    # Replace content between markers
    start_idx = content.find(start_marker) + len(start_marker)
    end_idx = content.find(end_marker)
    
    # Build new content
    new_content = (
        content[:start_idx] +
        "\n" + repos_table + "\n" +
        content[end_idx:]
    )
    
    # Remove old timestamp if it exists
    new_content = new_content.split("> *Last updated:")[0]
    
    # Add new update timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    new_content += f"\n> *Last updated: {timestamp}*"
    
    # Write back
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    num_repos = len([r for r in repos_table.split('|') if '**' in r])
    logger.info(f"✓ README updated successfully with {num_repos} repositories")
    return True


def main():
    """Main execution."""
    github_token = os.getenv("README_PAT")
    
    logger.info(f"Fetching repositories for {GITHUB_USERNAME}...")
    repos = get_user_repos(GITHUB_USERNAME, github_token)
    
    if not repos:
        logger.warning("No repositories found!")
        return
    logger.info(f"Found {len(repos)} repositories")
    logger.info(f"Repositories fetched: {repos}")
    repos_table = build_repos_table(repos)
    if update_readme(repos_table):
        logger.info("Done!")
    else:
        logger.error("Failed to update README")

if __name__ == "__main__":
    main()
