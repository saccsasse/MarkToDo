from test.utils import *
from app.routers.auth import *
from starlette import status
from jose import jwt
from datetime import timedelta
from fastapi import HTTPException
from app.routers.auth import bcrypt_context


app.dependency_overrides[get_db] = override_get_db


#----------AUTHENTICATION----------


def test_authenticate_user(test_user):
    db = TestingSessionLocal()

    authenticated_user = authenticate_user(test_user.username,'myadminpassword123', db)
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username

    non_existent_user = authenticate_user('wrongusername', 'myadminpassword123', db)
    assert non_existent_user is False

    wrong_password_user = authenticate_user(test_user.username, 'wrongpassword', db)
    assert wrong_password_user is False


#----------ACCESS_TOKEN----------


def test_create_access_token():
    username = 'testuser'
    user_id = 1
    role = 'user'
    expires_delta = timedelta(days=1)

    token = create_access_token(username, user_id, role, expires_delta)
    decoded_token = jwt.decode(token,SECRET_KEY,
                               algorithms=ALGORITHM,
                               options={'verify_signature': False})

    assert decoded_token['sub'] == username
    assert decoded_token['id'] == user_id
    assert decoded_token['role'] == role


#----------GET_CURRENT_USER----------


#pytest con not test async functionality!!! so we need to use child library called pytest-asyncio
@pytest.mark.asyncio
async def test_get_current_user():
    encode = {'sub': 'testuser', 'id': 1, 'role': 'admin'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    user = await get_current_user(token=token)
    assert user == {'username': 'testuser', 'id': 1, 'role': 'admin'}


@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {'role': 'user'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == 'Could not validate user'


#----------POST----------


def test_create_user(test_user):
    request_data = {
        'email': 'newemail@gmail.com',
        'username': 'newusername',
        'first_name': 'New First Name',
        'last_name': 'New Last Name',
        'role': 'user',
        'password': 'newpassword123',
    }
    response = client.post("/auth/", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    # Check if everything is fine in users db
    db = TestingSessionLocal()
    create_user_model = db.query(Users).filter(Users.id == 2).first()
    assert create_user_model.email == request_data.get('email')
    assert create_user_model.username == request_data.get('username')
    assert create_user_model.first_name == request_data.get('first_name')
    assert create_user_model.last_name == request_data.get('last_name')
    assert create_user_model.role == request_data.get('role')
    assert bcrypt_context.verify(request_data.get("password"), create_user_model.hashed_password)
