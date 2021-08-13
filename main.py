import random
import uuid
from datetime import timedelta

import uvicorn
from fastapi import Depends
from fastapi import FastAPI, Form
from fastapi import Request, Response
from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import Base
from database import SessionLocal
from database import engine
from models import create_todo
from models import delete_todo
from models import get_todo
from models import get_todos
from models import update_todo

Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/todos")
async def todos(request: Request, db: Session = Depends(get_db)):
    session_key = request.cookies.get("session_key", uuid.uuid4().hex)
    todos = get_todos(db, session_key)

    return todos

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    session_key = request.cookies.get("session_key", uuid.uuid4().hex)
    todos = get_todos(db, session_key)
    context = {
        "request": request,
        "todos": todos,
        "title": "Home"
    }
    response = templates.TemplateResponse("home.html", context)
    response.set_cookie(key="session_key", value=session_key, expires=259200)  # 3 days
    return response


@app.post("/add", response_class=HTMLResponse)
async def post_add(request: Request, content: str = Form(...), db: Session = Depends(get_db)):
    session_key = request.cookies.get("session_key")
    todo = create_todo(db, content=content, session_key=session_key)
    context = {"request": request, "todo": todo}
    return templates.TemplateResponse("todo/item.html", context)


@app.get("/edit/{item_id}", response_class=HTMLResponse)
async def get_edit(request: Request, item_id: int, db: Session = Depends(get_db)):
    todo = get_todo(db, item_id)
    context = {"request": request, "todo": todo}
    return templates.TemplateResponse("todo/form.html", context)


@app.put("/edit/{item_id}", response_class=HTMLResponse)
async def put_edit(request: Request, item_id: int, content: str = Form(...), db: Session = Depends(get_db)):
    todo = update_todo(db, item_id, content)
    context = {"request": request, "todo": todo}
    return templates.TemplateResponse("todo/item.html", context)


@app.delete("/delete/{item_id}", response_class=Response)
async def delete(item_id: int, db: Session = Depends(get_db)):
    delete_todo(db, item_id)


if __name__ == "__main__":
    """Run as module."""
    uvicorn.run(app, host="0.0.0.0", port=8000)
