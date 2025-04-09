# backend/admin.py

from sqladmin import Admin, ModelView
from backend.models import User
from backend.database import engine, async_session_maker  # Обрати внимание
from fastapi import FastAPI

app = FastAPI()
admin = Admin(app=app, engine=engine, session_maker=async_session_maker)

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.login]

