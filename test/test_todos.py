from test.utils import *

from fastapi import status
from app.main import app
from app.models.models import Todos
from app.routers.todos import get_db, get_current_user


#FastAPI will now use test DB + fake user for all endpoints
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


#----------GET----------


def test_read_all_authenticated(test_todo):
    response = client.get("/todo/read") #Sends GET request to your root endpoint.
    assert response.status_code == status.HTTP_200_OK #API should return success.
    assert response.json() == [{
        'id': test_todo.id,
        'title': 'Learn to code',
        'description': "Need to learn everyday",
        'priority': 5,
        'complete': False,
        'owner_id': 1
    }]


def test_read_one_authenticated(test_todo):
    response = client.get("/todo/read/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'id': test_todo.id,
        'title': 'Learn to code',
        'description': "Need to learn everyday",
        'priority': 5,
        'complete': False,
        'owner_id': 1
    }


def test_read_one_authenticated_not_found():
    response = client.get("/todo/read/999")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo is not found'}


#----------POST----------


def test_create_todo(test_todo):
    request_data = {
        'title': 'New Todo',
        'description': 'New Todo description',
        'priority': 5,
        'complete': False,
    }
    response = client.post('/todo/', json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    #Check if everything is fine in todos db
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')


#----------PUT----------


def test_update_todo(test_todo):
    request_data = {
        'title': 'Changed new todo\'s title',
        'description': 'New Todo description',
        'priority': 5,
        'complete': False,
    }

    response = client.put('/todo/1', json=request_data)
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model.title == 'Changed new todo\'s title'


def test_update_todo_not_found(test_todo):
    request_data = {
        'title': 'Changed new todo\'s title',
        'description': 'New Todo description',
        'priority': 5,
        'complete': False,
    }

    response = client.put('/todo/999', json=request_data)
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo is not found'}


#----------DELETE----------


def test_delete_todo(test_todo):
    response = client.delete('/todo/1')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


def test_delete_todo_not_found():
    response = client.delete('/todo/999')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo is not found'}
