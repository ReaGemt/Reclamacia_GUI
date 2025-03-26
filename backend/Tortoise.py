import asyncio
from tortoise import Tortoise
from backend.admin import Admin

async def create_admin():
    await Tortoise.init(db_url="sqlite://db.sqlite3", modules={"models": ["backend.admin"]})
    await Tortoise.generate_schemas()
    # Пример: username=admin, password=secret
    # В реальном проекте пароль стоит хэшировать!
    admin = await Admin.create(username="admin", password="secret")
    print("Admin created:", admin)

asyncio.run(create_admin())
