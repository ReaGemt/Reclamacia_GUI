from sqladmin import Admin
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from backend.database import engine  # ваш SQLAlchemy engine
from backend.models import User  # пример модели

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        if username == "admin" and password == "admin":
            request.session.update({"token": "secure-token"})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return "token" in request.session

# Здесь app должен быть передан из основного FastAPI-приложения
admin = None

def setup_admin(app):
    global admin
    admin = Admin(app=app, engine=engine, authentication_backend=AdminAuth())
