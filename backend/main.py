from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from selenium_worker import update_status

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/selenium")
def run_selenium_task(data: dict, background_tasks: BackgroundTasks):
    card_number = data.get("card_number")
    new_status = data.get("new_status")
    background_tasks.add_task(update_status, card_number, new_status)
    return {"message": "Selenium task started"}

# остальные маршруты и логика...