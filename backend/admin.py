from sqladmin import Admin, ModelView
from sqladmin.authentication import AdminAuthenticationBackend
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.requests import Request

from backend.models import User
from backend.app_instance import app  # ✅ заменили импорт

class AdminAuth(AdminAuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        return username == "admin" and password == "admin"

    async def logout(self, request: Request) -> bool:
        return True


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.login]


admin = Admin(
    app=app,
    authentication_backend=AdminAuth(secret_key="super-secret-key")
)

admin.add_view(UserAdmin)