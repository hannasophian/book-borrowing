import sqlite3
from ..models import Book, Member

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
                date_returned TEXT,
                UNIQUE(book_id)
            );
        """)
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
        connection.execute(
            "INSERT INTO books (title, author, isbn) VALUES (?, ?, ?)",
            (title, author, isbn)
        )
        cursor = connection.execute("SELECT * FROM books WHERE title = ? AND author = ?", (title, author))
        row = cursor.fetchone()
        if self.db_path != ":memory:":
            connection.close()
        return Book(id=row["id"], title=row["title"], author=row["author"], isbn=isbn)

    def add_member(self, name: str) -> Member:
        connection = self._connect()
        cursor = connection.execute(
            "INSERT INTO members (name) VALUES (?)",
            (name,)
        )
        if self.db_path != ":memory:":
            connection.close()
        return Member(id=cursor.lastrowid, name=name)
