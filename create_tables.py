from ai_news_aggregator.database.models import Base, engine

def setup():
    print("Creating database tables...")
    Base.metadata.create_all(engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    setup()