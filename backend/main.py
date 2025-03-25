from fastapi import FastAPI, HTTPException
from backend.database import init_db
from backend.models import Record, LoginRequest, CreateUserRequest
from backend import crud
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, BackgroundTasks
from backend.selenium_worker import update_status

app = FastAPI()
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/auth")
def authenticate_user(data: LoginRequest):
    if crud.check_user_credentials(data.login, data.password):
        return {"success": True}
    raise HTTPException(status_code=401, detail="Неверный логин или пароль")

@app.post("/users")
def create_user(data: CreateUserRequest):
    try:
        crud.create_user(data.login, data.password)
        return {"success": True}
    except Exception:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

@app.get("/records")
def get_records():
    return crud.get_all_records()

@app.post("/records")
def add_record(record: Record):
    return crud.create_record(record)

@app.put("/records/{record_id}")
def edit_record(record_id: int, record: Record):
    crud.update_record(record_id, record)
    return {"success": True}

@app.delete("/records/{record_id}")
def delete_record(record_id: int):
    crud.delete_record(record_id)
    return {"success": True}

@app.post("/selenium")
def run_selenium_task(data: dict, background_tasks: BackgroundTasks):
    card_number = data.get("card_number")
    new_status = data.get("new_status")
    background_tasks.add_task(update_status, card_number, new_status)
    return {"message": "Selenium task started"}