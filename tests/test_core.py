import unittest
from unittest.mock import patch, mock_open
import os
import sys
from pathlib import Path

# Add the 'code' directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'code'))

from core import build_repos_table, update_readme

class TestCore(unittest.TestCase):
    """Tests for core application logic."""

    def setUp(self):
        """Set up test data."""
        self.mock_repos = [
            {
                "name": "Repo2",
                "html_url": "http://github.com/user/repo2",
                "description": "Description for repo2",
                "language": "JavaScript",
                "stargazers_count": 20,
                "updated_at": "2023-01-02T00:00:00Z"
            },
            {
                "name": "Repo1",
                "html_url": "http://github.com/user/repo1",
                "description": "A very long description that will definitely need to be truncated.",
                "language": "Python",
                "stargazers_count": 10,
                "updated_at": "2023-01-01T00:00:00Z"
            }
        ]

    @patch('core.GITHUB_USERNAME', 'testuser')
    def test_build_repos_table(self):
        """Test the build_repos_table function sorts and formats correctly."""
        table = build_repos_table(self.mock_repos)
        # Repo2 should come first due to more stars
        self.assertIn("[**Repo2**]", table)
        self.assertIn("[**Repo1**]", table)
        self.assertTrue(table.find("Repo2") < table.find("Repo1"))
        # Check for description truncation
        self.assertIn("truncated...", table)
        self.assertNotIn("A very long description", table)

    def test_build_repos_table_no_repos(self):
        """Test the build_repos_table function with no repos."""
        table = build_repos_table([])
        self.assertEqual(table, "No repositories found.")

    @patch("core.open", new_callable=mock_open, read_data="<!-- START_REPOS -->\n<!-- END_REPOS -->\n<!--TIMESTAMP-->")
    @patch("core.README_FILE")
    def test_update_readme_success(self, mock_readme_file, mock_file):
        """Test the update_readme function successfully updates the file."""
        mock_readme_file.exists.return_value = True
        table_content = "| My Test Repo |"
        
        result = update_readme(table_content)
        
        self.assertTrue(result)
        mock_file.assert_called_with(mock_readme_file, "w", encoding="utf-8")
        
        # Get the content that was written to the file
        handle = mock_file()
        written_content = handle.write.call_args[0][0]
        
        self.assertIn(table_content, written_content)
        self.assertNotIn("<!--TIMESTAMP-->", written_content)

    @patch("core.README_FILE")
    def test_update_readme_file_not_found(self, mock_readme_file):
        """Test update_readme when the README file doesn't exist."""
        mock_readme_file.exists.return_value = False
        result = update_readme("any content")
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
