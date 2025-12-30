from test.utils import *
from starlette import status
from app.models.models import Todos
from app.routers.admin import get_db, get_current_user


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


#----------GET----------


def test_admin_read_all(test_todo):
    response = client.get("/admin/todo")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        'id': test_todo.id,
        'title': 'Learn to code',
        'description': "Need to learn everyday",
        'priority': 5,
        'complete': False,
        'owner_id': 1
    }]


#----------DELETE----------


def test_admin_delete_todo(test_todo):
    response = client.delete("/admin/todo/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


def test_admin_delete_todo_not_found():
    response = client.delete("/admin/todo/999")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo is not found'}
