import uvicorn
from fastapi import FastAPI
from sqladmin import Admin
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from backend.db import Base
from backend.admin import admin

app = FastAPI()

# Создание асинхронного движка
engine = create_async_engine("sqlite+aiosqlite:///./db.sqlite3")
SessionLocal = async_sessionmaker(bind=engine)

# Инициализация SQLAdmin
admin.init_app(app, engine)

@app.on_event("startup")
async def on_start():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True) 