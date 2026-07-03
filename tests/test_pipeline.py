import sys
import os
import pytest

# Add the project root to sys.path so it can find run_pipeline
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from run_pipeline import fetch_news

def test_fetch_news_connectivity():
    data = fetch_news("AI")
    assert isinstance(data, list)

def test_article_structure():
    data = fetch_news("Cloud Infrastructure")
    if len(data) > 0:
        assert 'title' in data[0]
        assert 'url' in data[0]
