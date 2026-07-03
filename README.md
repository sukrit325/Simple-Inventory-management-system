# FastAPI User Authentication & Management API

A production-ready REST API built with FastAPI, PostgreSQL, and SQLAlchemy. Features secure user registration, OAuth2 password flow authentication using JWT tokens, and password hashing.

---

## Prerequisites

Before setting up the project, ensure you have the following installed on your machine:
*   **Python 3.10+**
*   **PostgreSQL** (Ensure the service is running)

---

## Setup Instructions

### 1. Clone the Repository & Navigate to Project
```bash
cd your-repo-name
```
### 2. Create and activate a virtual environment

# Create the environment
```python
python -m venv venv
```

# Activate it (Mac/Linux)
```
source venv/bin/activate
```

# Activate it (Windows)
```
.\venv\Scripts\activate
```
### 3. Install requirements
 
```bash
pip install -r requirements.txt
```
### 4. Configure PostgreSQL Database
Log into your PostgreSQL instance and create a new database for the application:
```sql
CREATE DATABASE fastapi_db;
```
### 5. Environmental Variables Configuration
Create a .env file in the root directory of the project and populate it with your local configurations:
``` example snippet
DATABASE_URL="postgresql://DATABASE_USER:DATABASE_PASSWORD@localhost:5432/fastapi_db"
SECRET_KEY="your-super-secret-random-key-for-jwt-signing"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```
(Make sure to replace DATABASE_USER and DATABASE_PASSWORD with your actual Postgres credentials).
### 6. Running the Application
To spin up the local development server with auto-reload enabled:
```python
uvicorn main:app --reload
```
The application will be running locally at: http://localhost:8000
Interactive API Docs (Swagger UI): http://localhost:8000/docs

### Example API Requests
### 1. User Registration (Sign Up)
Creates a new user profile in the database.

Endpoint: POST /users/register

Content-Type: application/json
```bash 
curl -X 'POST' \
  'http://localhost:8000/users/register' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "johndoe",
  "email": "johndoe@example.com",
  "password": "secret123"
}'
```

### 2. User Login (Obtain Token)
Exchanges user credentials for a secure JWT access token using OAuth2 specification.

Endpoint: POST /users/login

Content-Type: application/x-www-form-urlencoded
``` bash
curl -X 'POST' \
  'http://localhost:8000/users/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=password&username=johndoe&password=secret123'
```
Expected Response
``` JSON
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```
### 3. Get Authenticated User Profile (Protected Route)
Fetches profile information for the currently logged-in user. Requires the Bearer token obtained from login.

Endpoint: GET /users/me
Content-Type: application/json
``` bash
curl -X 'GET' \
  'http://localhost:8000/users/me' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_ACTUAL_ACCESS_TOKEN_HERE'
```
