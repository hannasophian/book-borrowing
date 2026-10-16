from datetime import date
from unittest.mock import Mock

import pytest

from library.exceptions import BookAlreadyBorrowedError, BookNotFoundError, MemberNotFoundError
from library.service import LibraryService, LibraryDatabase
from library.models import Book, Member

def test_add_book_calls_database():
    mock_db = Mock()
    service = LibraryService(mock_db)
    
    service.add_book("1984", "George Orwell", "123")
    
    # Verify the database method was called
    mock_db.add_book.assert_called_once_with("1984", "George Orwell", "123")

def test_add_member_calls_database():
    mock_db = Mock()
    service = LibraryService(mock_db)
    
    service.add_member("John Doe")
    
    # Verify the database method was called
    mock_db.add_member.assert_called_once_with("John Doe")


def make_borrow_mock_db():
    mock_db = Mock()
    mock_db.get_member.return_value = Member(id="1", name="Alice")
    mock_db.get_book.return_value = Book(id="10", title="1984", author="George Orwell", isbn="123")
    return mock_db

def test_borrow_book_creates_loan():
    mock_db = make_borrow_mock_db()
    service = LibraryService(mock_db)

    loan = service.borrow_book("1", "10")

    mock_db.add_loan.assert_called_once_with("1", "10", date.today())
    assert loan == mock_db.add_loan.return_value

def test_borrow_book_unknown_member_raises():
    mock_db = make_borrow_mock_db()
    mock_db.get_member.return_value = None
    service = LibraryService(mock_db)

    with pytest.raises(MemberNotFoundError):
        service.borrow_book("1", "10")

    mock_db.add_loan.assert_not_called()

def test_borrow_book_unknown_book_raises():
    mock_db = make_borrow_mock_db()
    mock_db.get_book.return_value = None
    service = LibraryService(mock_db)

    with pytest.raises(BookNotFoundError):
        service.borrow_book("1", "10")

    mock_db.add_loan.assert_not_called()

def test_borrow_book_already_borrowed_raises():
    mock_db = make_borrow_mock_db()
    mock_db.add_loan.side_effect = BookAlreadyBorrowedError("Book 10 is already borrowed")
    service = LibraryService(mock_db)

    with pytest.raises(BookAlreadyBorrowedError):
        service.borrow_book("1", "10")
