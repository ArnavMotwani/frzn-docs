from sqlmodel import create_engine, Session
from app.core.config import settings

# Create the SQLModel/SQLAlchemy engine
engine = create_engine(settings.DATABASE_URL, echo=False)

# Dependency for FastAPI endpoints to get a session
def get_session():
    with Session(engine) as session:
        yield session