import uvicorn
from backend.app_instance import app
from backend.admin import admin
from backend.models import User
from sqladmin import ModelView
from sqladmin.authentication import AdminAuthenticationBackend
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Настройка БД
DATABASE_URL = "sqlite+aiosqlite:///db.sqlite3"
engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Подключаем SQLAdmin
admin.engine = engine
admin.init_app(app)

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)