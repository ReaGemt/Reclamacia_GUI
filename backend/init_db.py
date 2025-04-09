# backend/init_db.py

from backend.database import engine, Base
from backend import models  # <-- ОБЯЗАТЕЛЬНО: чтобы SQLAlchemy увидел все модели

import asyncio

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_models())
