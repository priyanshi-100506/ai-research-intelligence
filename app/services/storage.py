from sqlalchemy.dialects.postgresql import insert
from app.core.models import Article

class StorageService:
    def __init__(self, engine):
        self.engine = engine

    def save_articles(self, articles):
        # We use an 'ON CONFLICT DO NOTHING' approach
        # This handles the race condition gracefully at the database level
        with self.engine.begin() as conn:
            for a in articles:
                stmt = insert(Article).values(
                    article_id=a.article_id,
                    title=a.title,
                    url=a.url
                ).on_conflict_do_nothing(index_elements=['article_id'])
                conn.execute(stmt)
