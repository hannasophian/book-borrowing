
from datetime import date
from dataclasses import dataclass

@dataclass
class Book:
    id: str
    title: str
    author: str
    isbn: str | None

@dataclass
class Member:
    name: str
    id: str

@dataclass
class Loan:
    id: str
    member_id: str
    book_id: str
    date_borrowed: date
    date_returned: date | None

