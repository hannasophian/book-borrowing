from unittest.mock import Mock
from library.service import LibraryService, LibraryDatabase
from library.models import Book

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
