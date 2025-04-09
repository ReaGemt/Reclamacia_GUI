from fastapi import APIRouter, HTTPException
from sqlalchemy.future import select
from sqlalchemy import update, delete
from backend.models import User, Record, LoginRequest
from backend.database import async_session_maker
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/users")
async def get_user_logins():
    async with async_session_maker() as session:
        result = await session.execute(select(User.login))
        return [row[0] for row in result.fetchall()]


@router.post("/auth")
async def auth_user(request: LoginRequest):
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.login == request.login))
        user = result.scalar_one_or_none()
        if user and user.password_hash == request.password:  # Тут пока без хэша
            return {"message": "Authenticated"}
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")


@router.get("/records")
async def get_records():
    async with async_session_maker() as session:
        result = await session.execute(select(Record))
        records = result.scalars().all()
        return [r.__dict__ for r in records]


@router.post("/records")
async def create_record(record: Record):
    async with async_session_maker() as session:
        new_record = Record(**record.dict(exclude={"id"}))
        session.add(new_record)
        await session.commit()
        return {"message": "Record created"}


@router.put("/records/{record_id}")
async def update_record(record_id: int, record: Record):
    async with async_session_maker() as session:
        stmt = update(Record).where(Record.id == record_id).values(**record.dict(exclude={"id"}))
        result = await session.execute(stmt)
        await session.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Record not found")
        return {"message": "Record updated"}


@router.delete("/records/{record_id}")
async def delete_record(record_id: int):
    async with async_session_maker() as session:
        stmt = delete(Record).where(Record.id == record_id)
        result = await session.execute(stmt)
        await session.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Record not found")
        return {"message": "Record deleted"}


@router.post("/selenium")
async def update_status_via_selenium(data: dict):
    # Пока заглушка — просто возвращаем успех
    card_number = data.get("card_number")
    new_status = data.get("new_status")
    print(f"[Selenium-мок] Обновляем статус {card_number} → {new_status}")
    return JSONResponse(content={"message": "Selenium status updated"})

    # TODO: Реализовать обновление статуса через Selenium