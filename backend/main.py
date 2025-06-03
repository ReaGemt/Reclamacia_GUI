from fastapi import FastAPI
from backend.routes import router as api_router

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Reclamacia GUI API"}

app.include_router(api_router)

# Вставка отладочного запуска (опционально)
if __name__ == "__main__":
    from backend.selenium_worker import update_status
    print("▶ Запуск Selenium")
    update_status("RUD0000259991000", "Гарантия")
    print("✔ Завершение Selenium")