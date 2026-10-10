import pytest
from library.db.tables import LibraryDatabaseService
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
