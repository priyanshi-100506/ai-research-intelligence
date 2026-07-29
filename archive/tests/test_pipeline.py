import pytest
from unittest.mock import MagicMock
from app.core.models import Article
from app.services.storage import StorageService

def test_storage_save_articles():
    # Setup mock engine
    mock_engine = MagicMock()
    storage = StorageService(mock_engine)
    
    # Simulate some Article objects
    articles = [
        Article(article_id='1', title='Test 1', url='http://test1.com'),
        Article(article_id='2', title='Test 2', url='http://test2.com')
    ]
    
    # Trigger the save
    storage.save_articles(articles)
    
    # Assert that the engine's begin method was called (verifying the transaction started)
    assert mock_engine.begin.called