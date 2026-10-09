class Book:
    id: str
    title: str
    author: str
    isbn: str | None

class Member:
    name: str
    id: str

class Loan: 
    id: str
    member_id: str
    book_id: str
    date_borrowed: Date
    date_returned: Date | None

