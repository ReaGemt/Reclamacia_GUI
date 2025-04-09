import uvicorn
from fastapi import FastAPI
from fastapi_admin.app import app as admin_app
from fastapi_admin.providers.login import UsernamePasswordProvider
from fastapi_admin.models import AbstractAdmin
from fastapi_admin.resources import Model  # ✅ для версии 1.0.3
from tortoise import fields, models
from tortoise.contrib.fastapi import register_tortoise
import redis.asyncio as redis

app = FastAPI()

# Модель администратора
class Admin(AbstractAdmin):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    password = fields.CharField(max_length=128)

    class Meta:
        table = "admin"

# Модель пользователя (для панели)
class User(models.Model):
    id = fields.IntField(pk=True)
    login = fields.CharField(max_length=50, unique=True)
    password_hash = fields.CharField(max_length=128)

    def __str__(self):
        return self.login

# Подключение Tortoise ORM
register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={"models": ["__main__"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

# Ресурс пользователя (в виде объекта)
UserResource = Model(User)

# Функция инициализации панели
async def init_admin():
    redis_client = await redis.from_url("redis://localhost")

    await admin_app.configure(
        logo_url="https://example.com/logo.png",
        template_folders=[],
        redis=redis_client,
        providers=[
            UsernamePasswordProvider(
                admin_model=Admin,
                login_logo_url="https://example.com/logo.png",
            )
        ]
    )

    await admin_app.register_resources([UserResource])

# Запуск инициализации
@app.on_event("startup")
async def startup():
    await init_admin()

# Подключение панели
app.mount("/admin", admin_app)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002)