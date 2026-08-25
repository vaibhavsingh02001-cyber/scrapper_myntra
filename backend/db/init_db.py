from backend.db.database import engine, Base
from backend.models import Job, Result, QueryHistory

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database initialization complete.")

if __name__ == "__main__":
    init_db()
