import sqlite3
from datetime import date

import pytest
from library.db.tables import LibraryDatabaseService
from library.exceptions import BookAlreadyBorrowedError
from library.models import Book, Member


@pytest.fixture
def db():
    """Fixture that provides a fresh in-memory database for each test"""
    # :memory: creates a true in-memory database that's destroyed when closed
    db_instance = LibraryDatabaseService(":memory:")
    yield db_instance
    # Explicitly close to destroy the in-memory database
    db_instance.close()


def test_add_book(db):
    """Test adding a book to the database"""
    book = db.add_book("1984", "George Orwell", "978-0451524935")
    
    assert book.title == "1984"
    assert book.author == "George Orwell"
    assert book.isbn == "978-0451524935"
    assert book.id is not None


def test_add_member(db):
    """Test adding a member to the database"""
    member = db.add_member("Alice")
    
    assert member.name == "Alice"
    assert member.id is not None


def test_add_multiple_books(db):
    """Test adding multiple books"""
    book1 = db.add_book("1984", "George Orwell", "978-0451524935")
    book2 = db.add_book("Brave New World", "Aldous Huxley", "978-0060850524")
    
    assert book1.id != book2.id
    assert book1.title == "1984"
    assert book2.title == "Brave New World"


def test_add_multiple_members(db):
    """Test adding multiple members"""
    member1 = db.add_member("Alice")
    member2 = db.add_member("Bob")
    
    assert member1.id != member2.id
    assert member1.name == "Alice"
    assert member2.name == "Bob"


def test_tables_created_on_init(db):
    """Test that tables are created when database is initialized"""
    # If tables weren't created, these operations would fail
    db.add_book("Test", "Author", "123")
    db.add_member("Test Member")
    
    # If we get here without errors, tables were created successfully
    assert True


def test_get_book(db):
    """Test fetching a book by id"""
    added = db.add_book("1984", "George Orwell", "978-0451524935")

    assert db.get_book(added.id) == added


def test_get_book_not_found(db):
    """Test fetching a book that doesn't exist"""
    assert db.get_book(999) is None


def test_get_member(db):
    """Test fetching a member by id"""
    added = db.add_member("Alice")

    assert db.get_member(added.id) == added


def test_get_member_not_found(db):
    """Test fetching a member that doesn't exist"""
    assert db.get_member(999) is None


def test_add_loan(db):
    """Test creating a loan"""
    book = db.add_book("1984", "George Orwell", "978-0451524935")
    member = db.add_member("Alice")

    loan = db.add_loan(member.id, book.id, date(2026, 10, 16))

    assert loan.id is not None
    assert loan.member_id == member.id
    assert loan.book_id == book.id
    assert loan.date_borrowed == date(2026, 10, 16)
    assert loan.date_returned is None


def test_add_loan_book_already_borrowed(db):
    """Test that the same book can't be loaned twice"""
    book = db.add_book("1984", "George Orwell", "978-0451524935")
    alice = db.add_member("Alice")
    bob = db.add_member("Bob")
    db.add_loan(alice.id, book.id, date(2026, 10, 16))

    with pytest.raises(BookAlreadyBorrowedError):
        db.add_loan(bob.id, book.id, date(2026, 10, 17))


def test_add_loan_book_returned_can_be_borrowed_again(db):
    """Test that a returned book can be loaned again"""
    book = db.add_book("1984", "George Orwell", "978-0451524935")
    alice = db.add_member("Alice")
    bob = db.add_member("Bob")
    first_loan = db.add_loan(alice.id, book.id, date(2026, 10, 16))
    # Simulate returning the book until there is a return method
    connection = db._connect()
    connection.execute("UPDATE loans SET date_returned = ? WHERE id = ?", ("2026-10-20", first_loan.id))
    connection.commit()

    second_loan = db.add_loan(bob.id, book.id, date(2026, 10, 21))

    assert second_loan.id != first_loan.id
    assert second_loan.member_id == bob.id


def test_add_loan_unknown_member(db):
    """Test that a loan for a non-existent member is rejected by the foreign key"""
    book = db.add_book("1984", "George Orwell", "978-0451524935")

    with pytest.raises(sqlite3.IntegrityError):
        db.add_loan(999, book.id, date(2026, 10, 16))
