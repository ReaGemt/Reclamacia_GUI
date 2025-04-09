# backend/main.py

from backend.admin import app, admin, UserAdmin
from backend.database import engine

admin.add_view(UserAdmin)

@app.get("/")
def root():
    return {"message": "Admin panel works!"}
