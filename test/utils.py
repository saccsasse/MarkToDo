import pytest

from sqlalchemy import create_engine, text #creates SQLite in-memory test DB
from sqlalchemy.orm import sessionmaker #creates DB session factory
from sqlalchemy.pool import StaticPool #ensures SQLite runs in same connection
from fastapi.testclient import TestClient #allows calling your FastAPI endpoints like real HTTP requests

from app.main import app
from app.db.db import Base #SQLAlchemy base for creating tables
from app.models.models import Todos, Users
from app.routers.auth import bcrypt_context


SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}, #needed for SQLite + FastAPI
    poolclass= StaticPool, #ensures all tests share the same DB connection
)


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


#makes tests always act as an admin
def override_get_current_user():
    return {'username': 'admin', 'id': 1, 'user_role': 'admin'}


client = TestClient(app)


"""
A fixture is a reusable function that:
- prepares data or environment before test
- gives that data to the test
- cleans up after test
"""

@pytest.fixture
def test_todo():
    todo = Todos(
        title = "Learn to code",
        description = "Need to learn everyday",
        priority = 5,
        complete = False,
        owner_id = 1
    )

    db = TestingSessionLocal() #opens a new session to the test SQLite database
    db.add(todo) #adds the object to the SQLAlchemy session queue (not yet saved to DB)
    db.commit() #writes the todos object into the test database

    #Before yield = setup
    #After yield = cleanup
    yield todo

    #Clean database so each test starts with an empty todos table
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()


@pytest.fixture
def test_user():
    user = Users(
        username = "admin",
        email = "admin@gmail.com",
        first_name = 'Aliaksei',
        last_name = 'Ramanouski',
        role = 'admin',
        hashed_password = bcrypt_context.hash("myadminpassword123"),
    )

    db = TestingSessionLocal()
    db.add(user)
    db.commit()

    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()

