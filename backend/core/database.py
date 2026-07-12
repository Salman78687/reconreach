from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},  # SQLite only
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from models import lead  # noqa: F401 — ensures models are registered
    Base.metadata.create_all(bind=engine)
    _migrate_add_missing_columns()


def _migrate_add_missing_columns():
    """Add new columns to existing DBs without dropping data (SQLite safe)."""
    migrations = [
        "ALTER TABLE leads ADD COLUMN raw_analysis TEXT DEFAULT '{}'",
    ]
    with engine.connect() as conn:
        existing = {
            row[1]
            for row in conn.execute(
                __import__("sqlalchemy").text("PRAGMA table_info(leads)")
            )
        }
        for stmt in migrations:
            # Parse column name from ALTER TABLE statement
            col = stmt.split("ADD COLUMN")[1].strip().split()[0]
            if col not in existing:
                conn.execute(__import__("sqlalchemy").text(stmt))
                conn.commit()
