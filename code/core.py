#!/usr/bin/env python3
"""
Core logic for building and updating the README.
"""

import logging
from datetime import datetime

from config import GITHUB_USERNAME, README_FILE, REPO_START_MARKER, REPO_END_MARKER
from utils import format_language, get_emoji_for_repo

logger = logging.getLogger(__name__)

def build_repos_table(repos):
    """Build markdown table for repositories."""
    if not repos:
        return "No repositories found."
    
    # Filter out this repo itself and sort by stars then updated date
    repos = [r for r in repos if r["name"].lower() != GITHUB_USERNAME.lower()]
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
    
    # Split the content at the markers
    before_repos = content.split(start_marker)[0]
    after_repos = content.split(end_marker)[1]
    
    # Build new content
    new_content = (
        before_repos +
        start_marker +
        "\n" + repos_table + "\n" +
        end_marker +
        after_repos
    )
    
    # Update the timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    new_content = new_content.replace("<!--TIMESTAMP-->", timestamp)
    
    # Write back
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    num_repos = len([r for r in repos_table.split('|') if '**' in r])
    logger.info(f"✓ README updated successfully with {num_repos} repositories")
    return True
