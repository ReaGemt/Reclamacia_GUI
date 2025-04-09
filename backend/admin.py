from sqladmin import Admin, ModelView
from starlette.requests import Request
from sqladmin.authentication import AuthenticationBackend

from backend.models import User


class SimpleAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        return form.get("username") == "admin" and form.get("password") == "admin"

    async def authenticate(self, request: Request) -> bool:
        return True

    async def logout(self, request: Request) -> bool:
        return True


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.login]


def setup_admin(app, engine):
    admin = Admin(app=app, engine=engine, authentication_backend=SimpleAuth())
    admin.add_view(UserAdmin)
