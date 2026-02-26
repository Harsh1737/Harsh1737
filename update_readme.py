#!/usr/bin/env python3
"""
GitHub Profile README Updater
Automatically fetches repositories and updates the README with repo details.
"""

import json
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError

# Configuration
GITHUB_USERNAME = "Harsh1737"
README_FILE = "README.md"
REPO_START_MARKER = "<!-- START_REPOS -->"
REPO_END_MARKER = "<!-- END_REPOS -->"

def get_user_repos(username):
    """Fetch all public repositories for a GitHub user."""
    url = f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated&type=owner"
    
    try:
        with urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode('utf-8'))
    except URLError as e:
        print(f"Error fetching repos: {e}")
        return []

def get_emoji_for_repo(repo_name, description):
    """Assign emoji based on repository name/description."""
    name_lower = repo_name.lower()
    desc_lower = (description or "").lower()
    
    emojis = {
        "site": "🌐",
        "portfolio": "🌐",
        "dotfiles": "⚙️",
        "config": "⚙️",
        "youtube": "🎬",
        "video": "🎬",
        "git": "🔧",
        "chess": "♟️",
        "game": "🎮",
        "hackathon": "💡",
        "sih": "💡",
        "frontend": "🎨",
        "backend": "🔌",
        "api": "🔌",
    }
    
    for key, emoji in emojis.items():
        if key in name_lower or key in desc_lower:
            return emoji
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
    
    for repo in repos[:10]:  # Limit to top 10
        emoji = get_emoji_for_repo(repo["name"], repo["description"])
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
    readme_path = Path(README_FILE)
    
    if not readme_path.exists():
        print(f"Error: {README_FILE} not found!")
        return False
    
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Find the markers
    start_marker = REPO_START_MARKER
    end_marker = REPO_END_MARKER
    
    if start_marker not in content or end_marker not in content:
        print("Error: Repository markers not found in README!")
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
    
    # Add update timestamp
    new_content = new_content.replace(
        "<!-- END_REPOS -->",
        f"<!-- END_REPOS -->\n\n> *Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}*"
    )
    
    # Write back
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print(f"✓ README updated successfully with {len([r for r in repos_table.split('|') if '**' in r])} repositories")
    return True

def main():
    """Main execution."""
    print(f"Fetching repositories for {GITHUB_USERNAME}...")
    repos = get_user_repos(GITHUB_USERNAME)
    
    if not repos:
        print("No repositories found!")
        return
    
    print(f"Found {len(repos)} repositories")
    
    repos_table = build_repos_table(repos)
    
    if update_readme(repos_table):
        print("Done!")
    else:
        print("Failed to update README")

if __name__ == "__main__":
    main()
