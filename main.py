from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
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


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


# Модель книги
class Book(BaseModel):
    id: int
    title: str
    author: str
    year: Optional[int] = None


# Временное "хранилище" — список книг
books_db: List[Book] = []


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


# Добавить новую книгу
@app.post("/books", response_model=Book)
def create_book(book: Book):
    books_db.append(book)
    return book


# Обновить книгу по ID
@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: int, updated_book: Book):
    for i, book in enumerate(books_db):
        if book.id == book_id:
            books_db[i] = updated_book
            return updated_book
    raise HTTPException(status_code=404, detail="Книга не найдена")


# Удалить книгу по ID
@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    for i, book in enumerate(books_db):
        if book.id == book_id:
            del books_db[i]
            return {"message": "Книга удалена"}
    raise HTTPException(status_code=404, detail="Книга не найдена")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
