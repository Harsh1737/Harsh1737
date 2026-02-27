import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
import os
from urllib.error import URLError

# Make sure the script can find the functions from update_readme
from update_readme import (
    get_user_repos,
    get_emoji_for_repo,
    format_language,
    build_repos_table,
    update_readme,
)

# Sample API response for a single repository
SAMPLE_REPO = {
    "name": "test-repo",
    "html_url": "https://github.com/Harsh1737/test-repo",
    "description": "A test repository.",
    "language": "Python",
    "stargazers_count": 42,
    "updated_at": "2023-10-27T10:00:00Z",
}

# Sample README content
SAMPLE_README_CONTENT = """
# My Awesome Profile

<!-- START_REPOS -->
This will be replaced.
<!-- END_REPOS -->

Some other content.
"""

class TestReadmeUpdater(unittest.TestCase):

    @patch("update_readme.urlopen")
    def test_get_user_repos_success(self, mock_urlopen):
        """Tests successful fetching of user repositories."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps([SAMPLE_REPO]).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        repos = get_user_repos("Harsh1737")
        self.assertEqual(len(repos), 1)
        self.assertEqual(repos[0]["name"], "test-repo")
        print("\n✓ test_get_user_repos_success: OK")

    @patch("update_readme.urlopen", side_effect=URLError("Network error"))
    def test_get_user_repos_failure(self, mock_urlopen):
        """Tests failure in fetching user repositories."""
        repos = get_user_repos("Harsh1737")
        self.assertEqual(repos, [])
        print("✓ test_get_user_repos_failure: OK")

    def test_get_emoji_for_repo(self):
        """Tests the emoji selection logic."""
        self.assertEqual(get_emoji_for_repo("my-website", "portfolio"), "🌐")
        self.assertEqual(get_emoji_for_repo("dotfiles", ""), "⚙️")
        self.assertEqual(get_emoji_for_repo("video-app", ""), "🎬")
        self.assertEqual(get_emoji_for_repo("some-random-project", ""), "📦")
        print("✓ test_get_emoji_for_repo: OK")

    def test_format_language(self):
        """Tests the language formatting logic."""
        self.assertEqual(format_language("Python"), "`Python`")
        self.assertEqual(format_language(None), "—")
        print("✓ test_format_language: OK")

    def test_build_repos_table(self):
        """Tests the markdown table generation."""
        repos = [
            SAMPLE_REPO,
            {**SAMPLE_REPO, "name": "another-repo", "stargazers_count": 100}
        ]
        table = build_repos_table(repos)
        
        # Check for header
        self.assertIn("| &nbsp; | Repository | Description | Language | Stars |", table)
        # Check for correct ordering (most stars first)
        self.assertIn("another-repo", table.splitlines()[2])
        self.assertIn("test-repo", table.splitlines()[3])
        # Check for content
        self.assertIn("[**test-repo**]", table)
        self.assertIn("⭐ 42", table)
        self.assertIn("`Python`", table)
        print("✓ test_build_repos_table: OK")

    @patch("builtins.open", new_callable=mock_open, read_data=SAMPLE_README_CONTENT)
    @patch("update_readme.Path.exists", return_value=True)
    def test_update_readme(self, mock_exists, mock_file):
        """Tests the README file update process."""
        repos_table = build_repos_table([SAMPLE_REPO])
        
        # We need to capture what's being written to the file
        # The mock_open handle can do this for us.
        handle = mock_file()

        update_readme(repos_table)

        # Ensure open was called for writing
        mock_file.assert_called_with("README.md", "w", encoding="utf-8")
        
        # Get all the writes and join them
        written_content = "".join(call.args[0] for call in handle.write.call_args_list)

        self.assertIn("<!-- START_REPOS -->", written_content)
        self.assertIn("[**test-repo**]", written_content)
        self.assertIn("<!-- END_REPOS -->", written_content)
        self.assertNotIn("This will be replaced.", written_content)
        print("✓ test_update_readme: OK")


if __name__ == "__main__":
    print("Running tests for update_readme.py...")
    unittest.main()
