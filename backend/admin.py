import uvicorn
from fastapi import FastAPI
from fastapi_admin.app import app as admin_app
from fastapi_admin.providers.login import UsernamePasswordProvider
from fastapi_admin.models import AbstractAdmin
from tortoise import fields, models
from tortoise.contrib.fastapi import register_tortoise

app = FastAPI()

# Пример модели администратора (необходимо для входа в админку)
class Admin(AbstractAdmin):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    password = fields.CharField(max_length=128)

    class Meta:
        table = "admin"

# Пример модели для управления (например, пользователи)
class User(models.Model):
    id = fields.IntField(pk=True)
    login = fields.CharField(max_length=50, unique=True)
    password_hash = fields.CharField(max_length=128)

    def __str__(self):
        return self.login

# Инициализация Tortoise ORM для работы с SQLite
register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={"models": ["__main__"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

# Функция для настройки fastapi-admin
async def init_admin():
    await admin_app.configure(
        logo_url="https://example.com/logo.png",  # URL логотипа админки
        template_folders=[],  # можете указать папки с шаблонами, если нужно
        providers=[
            UsernamePasswordProvider(
                admin_model=Admin,
                login_logo_url="https://example.com/logo.png",
            )
        ],
    )

# Запускаем настройку админ-панели при старте приложения
@app.on_event("startup")
async def startup():
    await init_admin()

# Монтируем админ-панель по адресу /admin
app.mount("/admin", admin_app)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002)
