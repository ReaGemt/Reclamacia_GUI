# backend/models.py

from sqlalchemy import Column, Integer, String
from backend.database import Base
from pydantic import BaseModel

class Record(BaseModel):
    id: int | None = None
    record_date: str
    last_name: str
    first_name: str
    patronymic: str
    status: str
    comment: str
    card_number: str
    organization: str
    manufacturer: str
    work_status: str
    created_by: str

class LoginRequest(BaseModel):
    login: str
    password: str

class CreateUserRequest(BaseModel):
    login: str
    password: str

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
