# backend/main.py

from backend.admin import app, admin, UserAdmin
from backend.database import engine
from backend.routes import router as api_router

app.include_router(api_router)
admin.add_view(UserAdmin)

@app.get("/")
def root():
    return {"message": "Admin panel works!"}
