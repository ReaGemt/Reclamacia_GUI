import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from sqlalchemy.future import select
from sqlalchemy import update, delete
from backend.models import User, Record, RecordModel, LoginRequest
from backend.crud import hash_password
from backend.database import async_session_maker
from fastapi.responses import JSONResponse
from backend.selenium_worker import update_status

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("routes")


@router.get("/users")
async def get_user_logins():
    try:
        async with async_session_maker() as session:
            result = await session.execute(select(User.login))
            return [row[0] for row in result.fetchall()]
    except Exception as e:
        logger.exception("Ошибка при получении логинов пользователей")
        raise HTTPException(status_code=500, detail="Не удалось получить список пользователей")


@router.post("/auth")
async def auth_user(request: LoginRequest):
    try:
        async with async_session_maker() as session:
            result = await session.execute(select(User).where(User.login == request.login))
            user = result.scalar_one_or_none()
            if user and user.password_hash == hash_password(request.password):
                return {"message": "Успешная аутентификация"}
            raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    except HTTPException:
        raise
    except Exception:
        logger.exception("Ошибка при аутентификации")
        raise HTTPException(status_code=500, detail="Ошибка сервера при попытке аутентификации")


@router.get("/records")
async def get_records():
    try:
        async with async_session_maker() as session:
            result = await session.execute(select(RecordModel))
            records = result.scalars().all()
            return [r.__dict__ for r in records]
    except Exception as e:
        logger.exception("Ошибка при получении записей")
        raise HTTPException(status_code=500, detail="Не удалось получить записи")


@router.post("/records")
async def create_record(record: Record):
    try:
        async with async_session_maker() as session:
            new_record = RecordModel(**record.dict(exclude={"id"}))
            session.add(new_record)
            await session.commit()
            return {"message": "Запись создана"}
    except Exception as e:
        logger.exception("Ошибка при создании записи")
        raise HTTPException(status_code=500, detail="Не удалось создать запись")


@router.put("/records/{record_id}")
async def update_record(record_id: int, record: Record):
    try:
        async with async_session_maker() as session:
            stmt = update(RecordModel).where(RecordModel.id == record_id).values(**record.dict(exclude={"id"}))
            result = await session.execute(stmt)
            await session.commit()
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="Запись не найдена")
            return {"message": "Запись обновлена"}
    except Exception as e:
        logger.exception("Ошибка при обновлении записи")
        raise HTTPException(status_code=500, detail="Не удалось обновить запись")


@router.delete("/records/{record_id}")
async def delete_record(record_id: int):
    try:
        async with async_session_maker() as session:
            stmt = delete(RecordModel).where(RecordModel.id == record_id)
            result = await session.execute(stmt)
            await session.commit()
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="Запись не найдена")
            return {"message": "Запись удалена"}
    except Exception as e:
        logger.exception("Ошибка при удалении записи")
        raise HTTPException(status_code=500, detail="Не удалось удалить запись")


@router.post("/selenium")
async def update_status_via_selenium(data: dict, background_tasks: BackgroundTasks):
    try:
        card_number = data.get("card_number")
        new_status = data.get("new_status")
        background_tasks.add_task(update_status, card_number, new_status)
        return JSONResponse(content={"message": "Задача обновления статуса запущена в фоне"})
    except Exception as e:
        logger.exception("Ошибка при обновлении статуса через Selenium")
        raise HTTPException(status_code=500, detail="Ошибка при обновлении статуса через Selenium")
