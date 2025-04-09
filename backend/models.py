from sqlalchemy import Column, Integer, String
from backend.database import Base
from pydantic import BaseModel


# SQLAlchemy ORM-модель
class RecordORM(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True)
    record_date = Column(String)
    last_name = Column(String)
    first_name = Column(String)
    patronymic = Column(String)
    status = Column(String)
    comment = Column(String)
    card_number = Column(String)
    organization = Column(String)
    manufacturer = Column(String)
    work_status = Column(String)
    created_by = Column(String)


# Pydantic модель
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