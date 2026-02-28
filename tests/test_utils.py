import unittest
from unittest.mock import patch
import sys
from pathlib import Path

# Add the 'code' directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / 'code'))

from utils import format_language, get_emoji_for_repo

class TestUtils(unittest.TestCase):
    """Tests for utility functions."""

    def test_get_emoji_for_repo(self):
        """Test that get_emoji_for_repo returns a string."""
        self.assertIsInstance(get_emoji_for_repo(), str)
        self.assertGreater(len(get_emoji_for_repo()), 0)

    def test_format_language(self):
        """Test the format_language function."""
        self.assertEqual(format_language("Python"), "`Python`")
        self.assertEqual(format_language(None), "—")
        self.assertEqual(format_language(""), "—")

if __name__ == '__main__':
    unittest.main()
