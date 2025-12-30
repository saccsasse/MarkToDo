from fastapi import Depends, HTTPException, Path, APIRouter
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from typing import Annotated

from app.db.db import SessionLocal
from app.models.models import Todos
from app.routers.auth import get_current_user

router = APIRouter(
    prefix='/todo',
    tags=['todo']
)


def get_db():
    db = SessionLocal() #every request to the FastAPI must follow this line to open the db connection
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


#----------GET----------


@router.get("/read", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency,
                   db: db_dependency):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()


@router.get("/read/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency,
                    db: db_dependency,
                    todo_id: int = Path(gt=0)):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    todo_model = (db.query(Todos).filter(Todos.id == todo_id)\
                  .filter(Todos.owner_id == user.get('id')).first())
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo is not found")


#----------POST----------


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency,
                      db: db_dependency,
                      todo_request: TodoRequest):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    todo_model = Todos(**todo_request.model_dump(), owner_id = user.get('id'))
    db.add(todo_model)
    db.commit()
    return "Successfully created."


#----------PUT----------


@router.put("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency,
                      db: db_dependency,
                      todo_request: TodoRequest,
                      todo_id: int = Path(gt=0)):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    todo_model = (db.query(Todos).filter(Todos.id == todo_id)\
                  .filter(Todos.owner_id == user.get('id')).first())

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo is not found")

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()
    return "Successfully updated"


#----------DELETE----------


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency,
                      db: db_dependency,
                      todo_id: int = Path(gt=0)):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    todo_model = (db.query(Todos).filter(Todos.id == todo_id)\
                  .filter(Todos.owner_id == user.get('id')).first())

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo is not found")

    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).delete()
    db.commit()
    return "Successfully deleted"