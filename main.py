from fastapi import FastAPI, Query, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional

app=FastAPI()

#---------------- Data ----------------
books = [
    {"id": 1, "title": "Atomic Habits", "author": "James Clear", "genre": "Tech", "is_available": True},
    {"id": 2, "title": "Sapiens", "author": "Yuval Noah Harari", "genre": "History", "is_available": True},
    {"id": 3, "title": "1984", "author": "George Orwell", "genre": "Fiction", "is_available": True},
    {"id": 4, "title": "Brief History of Time", "author": "Stephen Hawking", "genre": "Science", "is_available": True},
    {"id": 5, "title": "Clean Code", "author": "Robert Martin", "genre": "Tech", "is_available": True},
    {"id": 6, "title": "The Alchemist", "author": "Paulo Coelho", "genre": "Fiction", "is_available": True},
]

borrow_records=[]
record_counter=1
queue=[]

#---------------- Home (Q1) ----------------
@app.get("/")
def home():
    return {"message": "Welcome to City Public Library"}

#---------------- Fixed routes ----------------
#Q2
@app.get("/books")
def get_books():
    available = sum(1 for b in books if b["is_available"])
    return {
        "total": len(books),
        "available_count": available,
        "books": books
    }

# Q5
@app.get("/books/summary")
def summary():
    total = len(books)
    available = sum(1 for b in books if b["is_available"])
    borrowed = total - available

    genre_count = {}
    for b in books:
        genre_count[b["genre"]] = genre_count.get(b["genre"], 0) + 1

    return {
        "total_books": total,
        "available": available,
        "borrowed": borrowed,
        "genre_breakdown": genre_count
    }

# Q10
@app.get("/books/filter")
def filter_books(
    genre: Optional[str] = None,
    author: Optional[str] = None,
    is_available: Optional[bool] = None
):
    result = books

    if genre is not None:
        result = [b for b in result if b["genre"].lower() == genre.lower()]

    if author is not None:
        result = [b for b in result if author.lower() in b["author"].lower()]

    if is_available is not None:
        result = [b for b in result if b["is_available"] == is_available]

    return {"count": len(result), "books": result}

# Q16
@app.get("/books/search")
def search_books(keyword: str):
    result = [
        b for b in books
        if keyword.lower() in b["title"].lower()
        or keyword.lower() in b["author"].lower()
    ]
    return {"total_found": len(result), "books": result}

# Q17
@app.get("/books/sort")
def sort_books(sort_by: str = "title", order: str = "asc"):
    valid = ["title", "author", "genre"]

    if sort_by not in valid:
        raise HTTPException(status_code=400, detail="Invalid sort field")

    reverse = True if order == "desc" else False

    sorted_books = sorted(books, key=lambda x: x[sort_by], reverse=reverse)

    return {
        "sorted_by": sort_by,
        "order": order,
        "books": sorted_books
    }

# Q18
@app.get("/books/page")
def paginate(page: int = 1, limit: int = 3):
    start = (page - 1) * limit
    end = start + limit

    total_pages = (len(books) + limit - 1) // limit

    return {
        "total": len(books),
        "total_pages": total_pages,
        "current_page": page,
        "limit": limit,
        "books": books[start:end]
    }

# Q20
@app.get("/books/browse")
def browse(
    keyword: Optional[str] = None,
    sort_by: str = "title",
    order: str = "asc",
    page: int = 1,
    limit: int = 3
):
    result = books

    if keyword:
        result = [
            b for b in result
            if keyword.lower() in b["title"].lower()
            or keyword.lower() in b["author"].lower()
        ]

    reverse = True if order == "desc" else False
    result = sorted(result, key=lambda x: x[sort_by], reverse=reverse)

    start = (page - 1) * limit
    end = start + limit

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "results": result[start:end]
    }

#---------------- BORROW RECORDS (Q4) ----------------

@app.get("/borrow-records")
def get_borrow_records():
    return {
        "total": len(borrow_records),
        "records": borrow_records
    }

# Q19 SEARCH + PAGE
@app.get("/borrow-records/search")
def search_records(member_name: str):
    result = [
        r for r in borrow_records
        if member_name.lower() in r["member_name"].lower()
    ]
    return {"results": result}

@app.get("/borrow-records/page")
def paginate_records(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    end = start + limit

    return {"records": borrow_records[start:end]}

#---------------- PYDANTIC MODELS (Q6, Q9) ----------------

class BorrowRequest(BaseModel):
    member_name: str = Field(..., min_length=2)
    book_id: int = Field(..., gt=0)
    borrow_days: int = Field(..., gt=0, le=30)
    member_id: str = Field(..., min_length=4)
    member_type: str = "regular"

class NewBook(BaseModel):
    title: str = Field(..., min_length=2)
    author: str = Field(..., min_length=2)
    genre: str = Field(..., min_length=2)
    is_available: bool = True

#---------------- HELPERS (Q7) ----------------

def find_book(book_id):
    for book in books:
        if book["id"] == book_id:
            return book
    return None

def calculate_due_date(days, member_type):
    if member_type == "premium":
        days = min(days, 60)
    else:
        days = min(days, 30)

    return f"Return by: Day {15 + days}"

#---------------- POST / BORROW (Q8) ----------------

@app.post("/borrow")
def borrow_book(req: BorrowRequest):
    global record_counter

    book = find_book(req.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if not book["is_available"]:
        raise HTTPException(status_code=400, detail="Already borrowed")

    book["is_available"] = False

    record = {
        "record_id": record_counter,
        "member_name": req.member_name,
        "book_id": req.book_id,
        "due_date": calculate_due_date(req.borrow_days, req.member_type)
    }

    borrow_records.append(record)
    record_counter += 1

    return record

#---------------- ADD BOOK (Q11) ----------------

@app.post("/books", status_code=201)
def add_book(book: NewBook):
    for b in books:
        if b["title"].lower() == book.title.lower():
            raise HTTPException(status_code=400, detail="Duplicate title")

    new_id = max(b["id"] for b in books) + 1
    new_book = book.dict()
    new_book["id"] = new_id

    books.append(new_book)
    return new_book

#---------------- QUEUE (Q14) ----------------

@app.post("/queue/add")
def add_to_queue(member_name: str, book_id: int):
    book = find_book(book_id)

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if book["is_available"]:
        raise HTTPException(status_code=400, detail="Book is available")

    queue.append({"member_name": member_name, "book_id": book_id})
    return {"message": "Added to queue"}

@app.get("/queue")
def get_queue():
    return queue

#---------------- RETURN (Q15) ----------------

@app.post("/return/{book_id}")
def return_book(book_id: int):
    book = find_book(book_id)

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    book["is_available"] = True

    for q in queue:
        if q["book_id"] == book_id:
            queue.remove(q)
            book["is_available"] = False
            return {"message": "returned and re-assigned"}

    return {"message": "returned and available"}

#---------------- VARIABLE ROUTES  ----------------

# Q3
@app.get("/books/{book_id}")
def get_book(book_id: int):
    book = find_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

# Q12
@app.put("/books/{book_id}")
def update_book(book_id: int, genre: Optional[str] = None, is_available: Optional[bool] = None):
    book = find_book(book_id)

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if genre is not None:
        book["genre"] = genre

    if is_available is not None:
        book["is_available"] = is_available

    return book

# Q13
@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    for i, b in enumerate(books):
        if b["id"] == book_id:
            removed = books.pop(i)
            return {"message": f"{removed['title']} deleted"}

    raise HTTPException(status_code=404, detail="Book not found")