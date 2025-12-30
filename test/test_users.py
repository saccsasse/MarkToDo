from test.utils import *
from starlette import status
from app.routers.users import get_db, get_current_user


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


#----------GET----------


def test_get_user(test_user):
    response = client.get("/users/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['id'] == test_user.id
    assert response.json()['username'] == 'admin'
    assert response.json()['email'] == 'admin@gmail.com'
    assert response.json()['first_name'] == 'Aliaksei'
    assert response.json()['last_name'] == 'Ramanouski'
    assert response.json()['role'] == 'admin'
    #we don't use one json because of hashed password


#----------PUT----------


def test_change_password(test_user):
    response = client.put("/users/password", json = {'password': 'myadminpassword123',
                                                     'new_password': 'newpassword'})
    assert response.status_code == status.HTTP_200_OK


def test_change_password_invalid_current_password(test_user):
    response = client.put("/users/password", json = {'password': 'wrongpassword',
                                                     'new_password': 'newpassword'})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Error on password change'}
