import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Assuming your FastAPI instance is in main.py and your SQLAlchemy Base is in database.py
from main import app
from database import Base, get_db

# 1. Setup an isolated, clean in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2. Override the production database dependency with our testing session
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    """Resets the database schema structure before running each individual test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# --- Basic Test Cases ---

def test_user_registration_success():
    """Tests creating a brand new user profile successfully."""
    response = client.post(
        "/users/register",
        json={"username": "testuser", "email": "test@example.com", "password": "supersecretpassword"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data


def test_user_registration_duplicate_username():
    """Verifies that the API blocks duplicate registrations."""
    payload = {"username": "cloneme", "email": "unique1@example.com", "password": "password123"}
    # First signup
    client.post("/users/register", json=payload)
    # Second signup with same username, different email
    payload["email"] = "unique2@example.com"
    response = client.post("/users/register", json=payload)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"


def test_login_oauth2_flow_success():
    """Verifies exchanging valid credentials for a functioning JWT access token."""
    # Seed a user to log in with
    client.post(
        "/users/register",
        json={"username": "authuser", "email": "auth@example.com", "password": "correctpassword"}
    )
    
    # Attempt login via form urlencoded data
    response = client.post(
        "/users/login",
        data={"grant_type": "password", "username": "authuser", "password": "correctpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials():
    """Verifies login fails gracefully with a 401 when given a bad password."""
    response = client.post(
        "/users/login",
        data={"grant_type": "password", "username": "nonexistent", "password": "wrongpassword"}
    )
    assert response.status_code == 401


def test_access_protected_profile_route():
    """Tests accessing a secured endpoint using a valid Bearer token."""
    # 1. Register and login to fetch token
    client.post(
        "/users/register",
        json={"username": "secureuser", "email": "secure@example.com", "password": "mypassword"}
    )
    login_response = client.post(
        "/users/login",
        data={"grant_type": "password", "username": "secureuser", "password": "mypassword"}
    )
    token = login_response.json()["access_token"]

    # 2. Request private resource using the Bearer header structure
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "secureuser"


def test_access_protected_route_unauthenticated():
    """Ensures unauthenticated requests to private routes fail with 401 Unauthorized."""
    response = client.get("/users/me")
    assert response.status_code == 401