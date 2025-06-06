import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.future import select
from sqlalchemy import update, delete
from backend.models import User, Record, RecordModel, Record, LoginRequest
from backend.crud import hash_password, verify_password
from backend.database import async_session_maker, get_async_session
from fastapi.responses import JSONResponse
from backend.selenium_worker import update_status

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("routes")


@router.get("/users", response_model=list[str])
async def get_user_logins(session=Depends(get_async_session)):
    try:
        result = await session.execute(select(User.login))
        return [row[0] for row in result.fetchall()]
    except Exception:
        logger.exception("Ошибка при получении логинов пользователей")
        raise HTTPException(status_code=500, detail="Не удалось получить список пользователей")


@router.post("/auth")
async def auth_user(request: LoginRequest, session=Depends(get_async_session)):
    try:
        result = await session.execute(select(User).where(User.login == request.login))
        user = result.scalar_one_or_none()
        if user and verify_password(request.password, user.password_hash):
            return {"message": "Успешная аутентификация"}
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    except HTTPException:
        raise
    except Exception:
        logger.exception("Ошибка при аутентификации")
        raise HTTPException(status_code=500, detail="Ошибка сервера при попытке аутентификации")


@router.get("/records")
async def get_records(session=Depends(get_async_session)):
    try:
        result = await session.execute(select(RecordModel))
        records = result.scalars().all()
        return [Record.from_orm(r) for r in records]
    except Exception:
        logger.exception("Ошибка при получении записей")
        raise HTTPException(status_code=500, detail="Не удалось получить записи")


@router.post("/records")
async def create_record(record: Record, session=Depends(get_async_session)):
    try:
        new_record = RecordModel(**record.dict(exclude={"id"}))
        session.add(new_record)
        await session.commit()
        return {"message": "Запись создана", "id": new_record.id}
    except Exception:
        logger.exception("Ошибка при создании записи")
        raise HTTPException(status_code=500, detail="Не удалось создать запись")


@router.put("/records/{record_id}")
async def update_record(record_id: int, record: Record, session=Depends(get_async_session)):
    try:
        stmt = update(RecordModel).where(RecordModel.id == record_id).values(**record.dict(exclude={"id"}))
        result = await session.execute(stmt)
        await session.commit()
        if not result.rowcount:
            raise HTTPException(status_code=404, detail="Запись не найдена")
        return {"message": "Запись обновлена"}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Ошибка при обновлении записи")
        raise HTTPException(status_code=500, detail="Не удалось обновить запись")


@router.delete("/records/{record_id}")
async def delete_record(record_id: int, session=Depends(get_async_session)):
    try:
        stmt = delete(RecordModel).where(RecordModel.id == record_id)
        result = await session.execute(stmt)
        await session.commit()
        if not result.rowcount:
            raise HTTPException(status_code=404, detail="Запись не найдена")
        return {"message": "Запись удалена"}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Ошибка при удалении записи")
        raise HTTPException(status_code=500, detail="Не удалось удалить запись")


@router.post("/selenium")
async def update_status_via_selenium(data: dict, background_tasks: BackgroundTasks):
    try:
        card_number = data.get("card_number")
        new_status = data.get("new_status")
        if not card_number or not new_status:
            raise HTTPException(status_code=400, detail="Не указаны card_number или new_status")
        background_tasks.add_task(update_status, card_number, new_status)
        return JSONResponse(content={"message": "Задача обновления статуса запущена в фоне"})
    except HTTPException:
        raise
    except Exception:
        logger.exception("Ошибка при обновлении статуса через Selenium")
        raise HTTPException(status_code=500, detail="Ошибка при обновлении статуса через Selenium")
