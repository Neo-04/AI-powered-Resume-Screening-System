from typing import Generator

from app.database.session import SessionLocal


def get_db() -> Generator:
    """Yield a database session and ensure it is closed afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
