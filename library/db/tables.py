import sqlite3
from datetime import date
from ..exceptions import BookAlreadyBorrowedError
from ..models import Book, Loan, Member

#TODO: rename
class LibraryDatabaseService:
    def __init__(self, db_path: str = "library.db") -> None:
        self.db_path = db_path
        self._connection = None
        self._create_tables()

    def _connect(self) -> sqlite3.Connection:
        # For in-memory databases, reuse the same connection
        if self.db_path == ":memory:" and self._connection:
            return self._connection
        
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        
        # Keep connection alive for in-memory databases
        if self.db_path == ":memory:":
            self._connection = connection
        
        return connection

    def _create_tables(self) -> None:
        connection = self._connect()
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT,
                available INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS loans (
                id INTEGER PRIMARY KEY,
                book_id INTEGER NOT NULL REFERENCES books(id),
                member_id INTEGER NOT NULL REFERENCES members(id),
                date_borrowed TEXT NOT NULL,
                date_returned TEXT
            );
        """)
        connection.commit()
        # Only close if it's a file-based database
        if self.db_path != ":memory:":
            connection.close()

    def close(self) -> None:
        """Close the connection (important for in-memory databases)"""
        if self._connection:
            self._connection.close()
            self._connection = None

    def __del__(self) -> None:
        """Cleanup when object is destroyed"""
        self.close()

    def add_book(self, title, author, isbn) -> Book:
        connection = self._connect()
        cursor = connection.execute(
            "INSERT INTO books (title, author, isbn) VALUES (?, ?, ?)",
            (title, author, isbn)
        )
        connection.commit()
        if self.db_path != ":memory:":
            connection.close()
        return Book(id=cursor.lastrowid, title=title, author=author, isbn=isbn)

    def add_member(self, name: str) -> Member:
        connection = self._connect()
        cursor = connection.execute(
            "INSERT INTO members (name) VALUES (?)",
            (name,)
        )
        connection.commit()
        if self.db_path != ":memory:":
            connection.close()
        return Member(id=cursor.lastrowid, name=name)

    def list_books(self) -> list[Book]:
        connection = self._connect()
        cursor = connection.execute("SELECT * FROM books")
        rows = cursor.fetchall()
        if self.db_path != ":memory:":
            connection.close()
        return [Book(id=row["id"], title=row["title"], author=row["author"], isbn=row["isbn"]) for row in rows]

    def get_book(self, book_id: str) -> Book | None:
        connection = self._connect()
        row = connection.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
        if self.db_path != ":memory:":
            connection.close()
        if row is None:
            return None
        return Book(id=row["id"], title=row["title"], author=row["author"], isbn=row["isbn"])

    def get_member(self, member_id: str) -> Member | None:
        connection = self._connect()
        row = connection.execute("SELECT * FROM members WHERE id = ?", (member_id,)).fetchone()
        if self.db_path != ":memory:":
            connection.close()
        if row is None:
            return None
        return Member(id=row["id"], name=row["name"])

    def add_loan(self, member_id: str, book_id: str, date_borrowed: date) -> Loan:
        connection = self._connect()
        try:
            # BEGIN IMMEDIATE takes the write lock before the check, so no other
            # connection can insert a loan for this book between the SELECT and INSERT
            connection.execute("BEGIN IMMEDIATE")
            active_loan = connection.execute(
                "SELECT 1 FROM loans WHERE book_id = ? AND date_returned IS NULL",
                (book_id,)
            ).fetchone()
            if active_loan is not None:
                raise BookAlreadyBorrowedError(f"Book {book_id} is already borrowed")
            cursor = connection.execute(
                "INSERT INTO loans (book_id, member_id, date_borrowed) VALUES (?, ?, ?)",
                (book_id, member_id, date_borrowed.isoformat())
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            if self.db_path != ":memory:":
                connection.close()
        return Loan(
            id=cursor.lastrowid,
            member_id=member_id,
            book_id=book_id,
            date_borrowed=date_borrowed,
            date_returned=None,
        )
