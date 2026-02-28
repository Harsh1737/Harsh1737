import unittest
from unittest.mock import patch, MagicMock
import os
import sys
from pathlib import Path

# Add the 'code' directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / 'code'))

from update_readme import build_repos_table, update_readme
from github_client import GitHubClient

class TestUpdateReadme(unittest.TestCase):

    def setUp(self):
        """Set up test data."""
        self.mock_repos = [
            {
                "name": "Repo1",
                "html_url": "http://github.com/user/repo1",
                "description": "Description for repo1",
                "language": "Python",
                "stargazers_count": 10,
                "updated_at": "2023-01-01T00:00:00Z"
            },
            {
                "name": "Repo2",
                "html_url": "http://github.com/user/repo2",
                "description": "Description for repo2",
                "language": "JavaScript",
                "stargazers_count": 20,
                "updated_at": "2023-01-02T00:00:00Z"
            }
        ]
        # Create a dummy README file
        self.readme_path = Path("README.md")
        with open(self.readme_path, "w") as f:
            f.write("<!-- START_REPOS -->\n<!-- END_REPOS -->\n<!--TIMESTAMP-->")

    def tearDown(self):
        """Clean up created files."""
        if os.path.exists(self.readme_path):
            os.remove(self.readme_path)

    @patch('update_readme.GITHUB_USERNAME', 'testuser')
    def test_build_repos_table(self):
        """Test the build_repos_table function."""
        table = build_repos_table(self.mock_repos)
        self.assertIn("Repo1", table)
        self.assertIn("Repo2", table)
        self.assertIn("Python", table)
        self.assertIn("JavaScript", table)

    @patch('github_client.urlopen')
    def test_github_client_get_user_repos(self, mock_urlopen):
        """Test the GitHubClient's get_user_repos method."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'[{"name": "test-repo"}]'
        mock_response.decode.return_value = '[{"name": "test-repo"}]'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        client = GitHubClient("testuser", "faketoken")
        repos = client.get_user_repos()

        self.assertEqual(len(repos), 1)
        self.assertEqual(repos[0]['name'], 'test-repo')
        mock_urlopen.assert_called_once()

    @patch('update_readme.README_FILE', Path("README.md"))
    def test_update_readme(self):
        """Test the update_readme function."""
        table = "| Test | Data |\n|---|---|"
        result = update_readme(table)
        self.assertTrue(result)
        with open(self.readme_path, "r") as f:
            content = f.read()
            self.assertIn(table, content)
            self.assertNotIn("<!--TIMESTAMP-->", content)

if __name__ == '__main__':
    unittest.main()
