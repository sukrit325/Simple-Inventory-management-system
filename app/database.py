import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import Engine

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()

# SQL scripts to intitialize the database schema and seed data

# DROP TABLE IF EXISTS users;

# CREATE TABLE users (
#     id SERIAL PRIMARY KEY,
#     username VARCHAR(50) NOT NULL UNIQUE,
#     email VARCHAR(100) NOT NULL UNIQUE,
#     hashed_password VARCHAR(255) NOT NULL,
#     is_active BOOLEAN DEFAULT TRUE,
#     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
# );

# -- Index optimization for login lookups
# CREATE INDEX idx_users_username ON users(username);
# CREATE INDEX idx_users_email ON users(email);