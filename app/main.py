from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from app.routers import users, items
from app.database import engine, Base, DATABASE_URL
from app import models

print("[STARTUP] Database URL:", DATABASE_URL)
print("[STARTUP] Creating tables if they don't exist")
try:
    Base.metadata.create_all(bind=engine)
    print("[STARTUP] Tables created successfully")
except Exception as e:
    print(f"[STARTUP] ERROR creating tables: {e}")


def ensure_item_table_columns():
    inspector = inspect(engine)
    if 'items' in inspector.get_table_names():
        existing_columns = {column['name'] for column in inspector.get_columns('items')}
        with engine.begin() as connection:
            if 'description' not in existing_columns:
                connection.execute(text('ALTER TABLE items ADD COLUMN description VARCHAR(255);'))
            if 'created_at' not in existing_columns:
                connection.execute(text('ALTER TABLE items ADD COLUMN created_at TIMESTAMP DEFAULT NOW();'))
                connection.execute(text('UPDATE items SET created_at = NOW() WHERE created_at IS NULL;'))


ensure_item_table_columns()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
print("[STARTUP] CORS middleware configured")

app.include_router(users.router)
app.include_router(items.router)
@app.get("/")
def read_root():
    print("[API] Root endpoint called")
    return{"message": "FastAPI backend is running succesfully!"}