📚 Library Book System - FastAPI Project

📌 Project Overview:
The Library Book Management System is a backend application developed using FastAPI that simulates real-world library operations. It allows users to manage books, borrow and return them, handle waiting queues, and perform advanced operations like search, sorting, and pagination. This project demonstrates how a scalable backend system is designed using REST APIs, data validation, and workflow handling.
This project was developed as part of an Internship Program.

🔧 Features:
📖 Book Management
- Get all books
- Add, update, delete books
- Book summary (total, available, borrowed, genre-wise)

🔄 Borrow & Return Workflow
- Borrow books with validation
- Due date calculation
- Return books with auto re-assignment (queue system)

⏳ Queue System
- Add users to queue if book unavailable
- Auto allocation when returned

🔍 Advanced APIs
- Search (title & author)
- Filter (genre, author, availability)
- Sorting (title, author, genre)
- Pagination
- Combined browse (search + sort + pagination)

🛠 Tech Stack:
- Python  
- FastAPI  
- Pydantic  
- Uvicorn
- Swagger UI

📂 Project Structure:
FastAPI-Library-System
│
├── main.py
├── requirements.txt
├── README.md
└── screenshots
      ├── Q1_home_route.png
      ├── Q2_get_all_books.png
      ├── Q3_get_book_by_id.png
      ├── ...
      └── Q20_browse_endpoint.png

▶️ How to Run:
1. Install dependencies
pip install -r requirements.txt

2. Run FastAPI server
uvicorn main:app --reload

3. Open Swagger UI
http://127.0.0.1:8000/docs
