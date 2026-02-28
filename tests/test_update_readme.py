import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
import os
import sys
from pathlib import Path
from urllib.error import URLError

# Add the 'code' directory to the Python path to find 'update_readme'
sys.path.insert(0, str(Path(__file__).parent.parent / 'code'))

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

# Sample README content reflecting the new structure
SAMPLE_README_CONTENT = """
# My Awesome Profile

<!-- START_REPOS -->
This will be replaced.
<!-- END_REPOS -->

> *This section is auto-updated by [GitHub Actions](.github/workflows/update-readme.yml). Last updated: <!--TIMESTAMP-->*

Some other content.
"""

class TestReadmeUpdater(unittest.TestCase):

    @patch("update_readme.urlopen")
    def test_get_user_repos_success(self, mock_urlopen):
        """Tests successful fetching of user repositories with and without a token."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps([SAMPLE_REPO]).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        # Test without a token
        repos_no_token = get_user_repos("Harsh1737")
        self.assertEqual(len(repos_no_token), 1)
        self.assertEqual(repos_no_token[0]["name"], "test-repo")

        # Test with a token
        repos_with_token = get_user_repos("Harsh1737", token="fake-token")
        self.assertEqual(len(repos_with_token), 1)
        self.assertEqual(repos_with_token[0]["name"], "test-repo")
        print("\n✓ test_get_user_repos_success: OK")

    @patch("update_readme.urlopen", side_effect=URLError("Network error"))
    def test_get_user_repos_failure(self, mock_urlopen):
        """Tests failure in fetching user repositories."""
        repos = get_user_repos("Harsh1737")
        self.assertEqual(repos, [])
        print("✓ test_get_user_repos_failure: OK")

    def test_get_emoji_for_repo(self):
        """Tests the simplified emoji selection logic."""
        self.assertEqual(get_emoji_for_repo(), "📦")
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
        
        self.assertIn("| &nbsp; | Repository | Description | Language | Stars |", table)
        self.assertIn("another-repo", table.splitlines()[2])
        self.assertIn("test-repo", table.splitlines()[3])
        self.assertIn("[**test-repo**]", table)
        self.assertIn("⭐ 42", table)
        self.assertIn("`Python`", table)
        print("✓ test_build_repos_table: OK")

    @patch("builtins.open", new_callable=mock_open, read_data=SAMPLE_README_CONTENT)
    @patch("update_readme.README_FILE.exists", return_value=True)
    def test_update_readme(self, mock_exists, mock_file):
        """Tests the README file update process."""
        repos_table = build_repos_table([SAMPLE_REPO])
        
        handle = mock_file()
        update_readme(repos_table)

        mock_file.assert_called_with(mock_file(), "w", encoding="utf-8")
        
        written_content = "".join(call.args[0] for call in handle.write.call_args_list)

        self.assertIn("<!-- START_REPOS -->", written_content)
        self.assertIn("[**test-repo**]", written_content)
        self.assertIn("<!-- END_REPOS -->", written_content)
        self.assertNotIn("This will be replaced.", written_content)
        self.assertNotIn("<!--TIMESTAMP-->", written_content)
        self.assertIn("Some other content.", written_content)
        print("✓ test_update_readme: OK")


if __name__ == "__main__":
    print("Running tests for update_readme.py...")
    unittest.main()
