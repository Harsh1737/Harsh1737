#!/usr/bin/env python3
"""
Utility functions for the README updater.
"""

def get_emoji_for_repo():
    """Returns a standard emoji for a repository."""
    return "📦"

def format_language(language):
    """
    Formats the language string for display.
    Returns '—' for None and wraps others in backticks.
    """
    if not language:
        return "—"
    return f"`{language}`"
