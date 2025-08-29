import sqlite3
import os
from datetime import datetime

def init_db():
    # Ensure we're using the correct path for the database
    db_path = os.path.join(os.path.dirname(__file__), 'library.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Create Books table
    c.execute('''CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        isbn TEXT UNIQUE,
        category TEXT,
        status TEXT DEFAULT 'available' CHECK(status IN ('available', 'borrowed', 'maintenance')),
        location TEXT,
        added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Create Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        address TEXT,
        membership_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive', 'suspended')),
        borrowed_books INTEGER DEFAULT 0
    )''')
    
    # Create BorrowRecords table
    c.execute('''CREATE TABLE IF NOT EXISTS borrow_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        borrow_date DATE NOT NULL,
        due_date DATE NOT NULL,
        return_date DATE,
        late_fee REAL DEFAULT 0.0,
        status TEXT DEFAULT 'borrowed' CHECK(status IN ('borrowed', 'returned', 'overdue')),
        FOREIGN KEY (book_id) REFERENCES books (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    # Add sample books
    sample_books = [
        ('The Great Gatsby', 'F. Scott Fitzgerald', '9780743273565', 'Fiction', 'available', 'Section A-1'),
        ('To Kill a Mockingbird', 'Harper Lee', '9780446310789', 'Fiction', 'available', 'Section A-2'),
        ('1984', 'George Orwell', '9780451524935', 'Fiction', 'available', 'Section A-3'),
        ('The Hobbit', 'J.R.R. Tolkien', '9780547928227', 'Fantasy', 'available', 'Section B-1'),
        ('Pride and Prejudice', 'Jane Austen', '9780141439518', 'Romance', 'available', 'Section B-2')
    ]
    
    c.execute('SELECT COUNT(*) FROM books')
    if c.fetchone()[0] == 0:
        c.executemany('''INSERT INTO books 
            (title, author, isbn, category, status, location) 
            VALUES (?, ?, ?, ?, ?, ?)''', sample_books)
    
    # Add sample users
    sample_users = [
        ('John Doe', 'john@example.com', '555-0101', '123 Main St'),
        ('Jane Smith', 'jane@example.com', '555-0102', '456 Oak Ave'),
        ('Bob Wilson', 'bob@example.com', '555-0103', '789 Pine Rd')
    ]
    
    c.execute('SELECT COUNT(*) FROM users')
    if c.fetchone()[0] == 0:
        c.executemany('''INSERT INTO users 
            (name, email, phone, address) 
            VALUES (?, ?, ?, ?)''', sample_users)
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
