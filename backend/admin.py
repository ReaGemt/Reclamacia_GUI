from sqladmin import Admin, ModelView
from fastapi import Request
from sqladmin.authentication import AuthenticationBackend
from backend.db import User, AdminUser


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        return True  # Без логина для простоты

    async def logout(self, request: Request) -> bool:
        return True

    async def authenticate(self, request: Request) -> bool:
        return True


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
