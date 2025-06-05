import asyncio
import os
import tempfile
import sqlite3

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from backend.main import app
from backend import database, routes, config, crud


@pytest.fixture
def client(tmp_path):
    # Temporary SQLite file
    db_path = tmp_path / "test.db"

    # Patch configuration for sync connections
    config.DB_PATH = str(db_path)

    # Create async engine bound to temporary database
    url = f"sqlite+aiosqlite:///{db_path}"
    engine = create_async_engine(url, echo=False)
    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Patch database and routes session maker
    database.engine = engine
    database.async_session_maker = Session
    routes.async_session_maker = Session

    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(database.Base.metadata.create_all)

    asyncio.run(init_models())

    with TestClient(app) as c:
        yield c


def test_auth(client):
    # Add user using hashed password
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    hashed = crud.hash_password("secret")
    cursor.execute(
        "INSERT INTO users (login, password_hash) VALUES (?, ?)",
        ("alice", hashed),
    )
    conn.commit()
    conn.close()

    # Correct credentials (hashed password expected by API)
    resp = client.post("/auth", json={"login": "alice", "password": hashed})
    assert resp.status_code == 200

    # Wrong password
    resp = client.post("/auth", json={"login": "alice", "password": "bad"})
    assert resp.status_code == 401
