import unittest
from unittest.mock import patch, MagicMock
import json
import sys
from pathlib import Path

# Add the 'code' directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'code'))

from github_client import GitHubClient

class TestGitHubClient(unittest.TestCase):
    """Tests for the GitHub API client."""

    @patch('github_client.urlopen')
    def test_get_user_repos_success(self, mock_urlopen):
        """Test successfully fetching user repositories."""
        mock_data = [{"name": "repo1"}, {"name": "repo2"}]
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(mock_data).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        client = GitHubClient("testuser", "faketoken")
        repos = client.get_user_repos()

        self.assertEqual(len(repos), 2)
        self.assertEqual(repos[0]["name"], "repo1")
        mock_urlopen.assert_called_once()
        # Check that the token is in the headers
        request_args = mock_urlopen.call_args[0][0]
        self.assertEqual(request_args.headers["Authorization"], "token faketoken")

    @patch('github_client.urlopen')
    def test_get_user_repos_no_token(self, mock_urlopen):
        """Test fetching repos without a token."""
        mock_data = [{"name": "repo1"}]
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(mock_data).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        client = GitHubClient("testuser")
        client.get_user_repos()

        request_args = mock_urlopen.call_args[0][0]
        self.assertNotIn("Authorization", request_args.headers)

    @patch('github_client.urlopen', side_effect=Exception("API Error"))
    def test_get_user_repos_failure(self, mock_urlopen):
        """Test failure when fetching user repositories."""
        client = GitHubClient("testuser", "faketoken")
        repos = client.get_user_repos()
        self.assertEqual(repos, [])

if __name__ == '__main__':
    unittest.main()
