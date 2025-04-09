from sqladmin import Admin, ModelView
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqladmin.authentication import AuthenticationBackend
from fastapi import Request
from starlette.responses import RedirectResponse
from backend.db import User, AdminUser  # модели перенесём в отдельный файл db.py


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        # Простой вход (можно доработать хеширование и проверку)
        return username == "admin" and password == "admin"

    async def logout(self, request: Request) -> bool:
        return True

    async def authenticate(self, request: Request) -> bool:
        return True  # Пропустить для простоты


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.login]
    name = "User"
    name_plural = "Users"


class AdminUserAdmin(ModelView, model=AdminUser):
    column_list = [AdminUser.id, AdminUser.username]
    name = "Admin"
    name_plural = "Admins"


admin = Admin(authentication_backend=AdminAuth())
admin.add_view(UserAdmin)
admin.add_view(AdminUserAdmin)
