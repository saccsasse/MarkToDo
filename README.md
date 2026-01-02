## Project Overview

This project is a portfolio-ready backend API for managing todos:

- Users can **create, read, update, and delete their own todos**.  
- Admins can **view and delete todos from any user**.  
- JWT-based authentication secures all endpoints.  
- Includes **secure password hashing** and **role-based access control**.  
- Fully tested using **pytest** with a separate SQLite test database.  

The application demonstrates best practices in **FastAPI architecture**, **dependency injection**, and **database management**.

---

## Tech Stack

- **Backend Framework:** FastAPI  
- **Database:** PostgreSQL (SQLAlchemy ORM)  
- **Migrations:** Alembic  
- **Authentication:** JWT tokens (HS256)  
- **Password Hashing:** bcrypt via Passlib  
- **Testing:** Pytest + FastAPI TestClient + SQLite  
- **Python Version:** 3.11+  

---

## Features

- User Registration & Login  
- JWT Authentication & Role-based Authorization (`user`, `admin`)  
- CRUD operations for todos:  
  - Users can manage their own todos  
  - Admins can manage all todos  
- User account management:  
  - View profile  
  - Change password  
- Database migrations with Alembic  
- Automated tests for all endpoints  

---

## Setup & Installation

git clone <repository_url>
cd <repository_folder>
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt

Default connection in app/db/db.py:
postgresql://postgres:mypassword123@localhost/TodoApplicationDatabase

alembic upgrade head
uvicorn app.main:app --reload

Health check

GET /healthy
Response: {"status": "Healthy"}

Tables:
Users: id, username, email, hashed_password, role, is_active
Todos: id, title, description, priority, complete, owner_id

Alembic migrations for version control:
alembic revision --autogenerate -m "Your message"
alembic upgrade head


## Authentication & Authorization

JWT-based authentication (HS256)
Access token expires after 20 minutes
Passwords hashed with bcrypt

Roles:
user: CRUD access to own todos
admin: Can view/delete all todos

Secure dependencies:
get_current_user()  # Returns username, id, and role


## Testing

Framework: Pytest + TestClient
Test database: SQLite (in-memory or file-based)
Fixtures: Pre-created users & todos, auto-cleanup after tests

Run tests
pytest


Tests cover:
User todos CRUD
Admin endpoints
Auth and JWT token handling
Password changes


##Usage Examples

Register a user
POST /auth/
{
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "secret123",
  "role": "user"
}

Login
POST /auth/token
Form data:
username=john_doe
password=secret123

Response:
{
  "access_token": "<jwt_token>",
  "token_type": "bearer"
}

Create a todo
POST /todo/
Authorization: Bearer <jwt_token>
{
  "title": "Learn FastAPI",
  "description": "Complete FastAPI tutorial",
  "priority": 5,
  "complete": false
}

Admin delete todo
DELETE /admin/todo/1
Authorization: Bearer <admin_token>
