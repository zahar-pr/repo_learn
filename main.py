from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене лучше указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory="."), name="static")

templates = Jinja2Templates(directory=".")


# Модель книги
class Book(BaseModel):
    id: int
    title: str
    author: str
    year: Optional[int] = None


# Временное "хранилище" — список книг
books_db: List[Book] = []
# эту строку нужно удалить

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "books": books_db}
    )


# Получить список всех книг
@app.get("/books", response_model=List[Book])
def get_books():
    return books_db


# Получить одну книгу по ID
@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    for book in books_db:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Книга не найдена")


@app.post("/books")
async def create_book(
    id: int = Form(...),
    title: str = Form(...),
    author: str = Form(...),
    year: Optional[int] = Form(None),
):
    book = Book(id=id, title=title, author=author, year=year)
    books_db.append(book)
    return RedirectResponse(url="/", status_code=303)


@app.get("/books/{book_id}/edit", response_class=HTMLResponse)
async def edit_book_form(request: Request, book_id: int):
    for book in books_db:
        if book.id == book_id:
            return templates.TemplateResponse(
                "edit.html", {"request": request, "book": book}
            )
    raise HTTPException(status_code=404, detail="Книга не найдена")


@app.post("/books/{book_id}/edit")
async def edit_book(
    book_id: int,
    id: int = Form(...),
    title: str = Form(...),
    author: str = Form(...),
    year: Optional[int] = Form(None),
):
    for i, book in enumerate(books_db):
        if book.id == book_id:
            books_db[i] = Book(id=id, title=title, author=author, year=year)
            return RedirectResponse(url="/", status_code=303)
    raise HTTPException(status_code=404, detail="Книга не найдена")


@app.post("/books/{book_id}/delete")
async def delete_book(book_id: int):
    for i, book in enumerate(books_db):
        if book.id == book_id:
            del books_db[i]
            return RedirectResponse(url="/", status_code=303)
    raise HTTPException(status_code=404, detail="Книга не найдена")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
