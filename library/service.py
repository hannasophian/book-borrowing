"""
Library Service Layer

This module contains the business logic for the library management system.

Actions: borrow, return, search, list, add_book, add_member
"""

from datetime import date
from typing import Protocol
from .exceptions import BookNotFoundError, MemberNotFoundError
from .models import Book, Loan, Member

class LibraryDatabase(Protocol):
    def add_book(self, title: str, author: str, isbn: str) -> Book : ...
    def get_book(self, book_id: str) -> Book | None: ...
    # def update_book(self, book: Book) -> None: ...

    def add_member(self, name: str) -> Member : ...
    def list_books(self) -> list[Book]: ...
    def get_member(self, member_id: str) -> Member | None: ...

    # Raises BookAlreadyBorrowedError if the book already has a loan
    def add_loan(self, member_id: str, book_id: str, date_borrowed: date) -> Loan: ...
    
class LibraryService:
    def __init__(self, database: LibraryDatabase):
        self.database = database
    
    def borrow_book(self, member_id: str, book_id: str) -> Loan:
        if self.database.get_member(member_id) is None:
            raise MemberNotFoundError(f"Member {member_id} not found")
        if self.database.get_book(book_id) is None:
            raise BookNotFoundError(f"Book {book_id} not found")
        return self.database.add_loan(member_id, book_id, date.today())
    
    # def return_book(self, member_id: str, book_id: str):
    #     pass
    
    def list_books(self):
        return self.database.list_books()
    
    def add_book(self, title: str, author: str, isbn: str) -> Book:
        return self.database.add_book(title, author, isbn)
    
    def add_member(self, name: str) -> Member:
        return self.database.add_member(name)
