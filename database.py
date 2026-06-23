"""
database.py — Database Configuration Module for CLINICOM
=========================================================
Provides the database engine, session factory, and ORM base class.

Configuration:
    Set USE_MOCK = True  for SQLite in-memory database (no server needed).
    Set USE_MOCK = False for MySQL production database (requires MySQL server).
"""

import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ──────────────────────────────────────────────
#  DATABASE MODE TOGGLE
#  Set to True  → SQLite in-memory (demo/presentation)
#  Set to False → MySQL server    (production)
# ──────────────────────────────────────────────
USE_MOCK = True

if USE_MOCK:
    # ── SQLite in-memory: runs instantly, no setup needed ──
    DATABASE_URL = "sqlite:///clinicom_demo.db"
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},  # Required for SQLite + threads
    )
else:
    # ── MySQL production mode ──
    from urllib.parse import quote_plus
    from dotenv import load_dotenv

    load_dotenv()

    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_NAME = os.getenv("DB_NAME", "clinicom")

    DATABASE_URL = (
        f"mysql+mysqlconnector://{DB_USER}:{quote_plus(DB_PASSWORD)}"
        f"@{DB_HOST}/{DB_NAME}"
    )
    engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)


# Session factory — creates new session instances
SessionLocal = sessionmaker(bind=engine)

# Declarative base — all ORM models inherit from this
Base = declarative_base()


def init_db():
    """Create all tables defined by models that inherit from Base.

    This is safe to call multiple times — existing tables are not modified.
    Must be called AFTER all model modules have been imported so that
    Base.metadata has the full table registry.
    """
    Base.metadata.create_all(engine)


@contextmanager
def get_session():
    """Provide a transactional database session with automatic cleanup.

    Usage:
        with get_session() as session:
            session.add(some_object)
            # auto-commits on success, auto-rolls-back on exception
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
