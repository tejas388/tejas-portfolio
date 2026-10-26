import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# Predictable backend/data directory for SQLite persistence
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_DB_FILE = DATA_DIR / "portfolio.db"

env_db_url = os.getenv("DATABASE_URL")
if not env_db_url:
    DATABASE_URL = f"sqlite:///{DEFAULT_DB_FILE}"
elif env_db_url.startswith("postgres://"):
    # Render, Heroku, and Neon provide postgres:// or postgresql://; SQLAlchemy 2.0 requires postgresql+psycopg:// for psycopg3
    DATABASE_URL = env_db_url.replace("postgres://", "postgresql+psycopg://", 1)
elif env_db_url.startswith("postgresql://") and not env_db_url.startswith("postgresql+"):
    DATABASE_URL = env_db_url.replace("postgresql://", "postgresql+psycopg://", 1)
elif env_db_url in ("sqlite:///./portfolio.db", "sqlite:///portfolio.db"):
    DATABASE_URL = f"sqlite:///{DEFAULT_DB_FILE}"
elif env_db_url.startswith("sqlite:///./data/"):
    # Ensure relative ./data/ path resolves cleanly to DATA_DIR
    filename = env_db_url.replace("sqlite:///./data/", "")
    DATABASE_URL = f"sqlite:///{DATA_DIR / filename}"
else:
    DATABASE_URL = env_db_url

# Ensure parent directory exists for any SQLite path
if DATABASE_URL.startswith("sqlite:////"):
    sqlite_path = Path(DATABASE_URL.replace("sqlite:////", "/"))
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
elif DATABASE_URL.startswith("sqlite:///"):
    sqlite_path = Path(DATABASE_URL.replace("sqlite:///", ""))
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)

is_sqlite = DATABASE_URL.startswith("sqlite")

if is_sqlite:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True
    )
else:
    # PostgreSQL pooling optimized for Render Free web service + Neon serverless PostgreSQL
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=5,
        max_overflow=5
    )

if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
