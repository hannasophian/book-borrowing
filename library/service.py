"""
Library Service Layer

This module contains the business logic for the library management system.

Actions: borrow, return, search, list, add_book, add_member
"""

from typing import Protocol
from .models import Book, Member

class LibraryDatabase(Protocol):
    def add_book(self, title: str, author: str, isbn: str) -> Book : ...
    # def get_book(self, book_id: int) -> Book | None: ...
    # def update_book(self, book: Book) -> None: ...

    def add_member(self, name: str) -> Member : ...
    def list_books(self) -> list[Book]: ...
    # def get_member(self, member_id: int) -> Member | None: ...

    # def add_loan(self, loan: Loan) -> None: ...
    # def get_loan_by_book(self, book_id: int) -> Loan | None: ...
    # def delete_loan(self, loan_id: int) -> None: ...

class LibraryService:
    def __init__(self, database: LibraryDatabase):
        self.database = database
    
    # def borrow_book(self, member_id: str, book_id: str):
    #     pass
    
    # def return_book(self, member_id: str, book_id: str):
    #     pass
    
    def list_books(self):
        return self.database.list_books()
    
    def add_book(self, title: str, author: str, isbn: str) -> Book:
        return self.database.add_book(title, author, isbn)
    
    def add_member(self, name: str) -> Member:
        return self.database.add_member(name)
