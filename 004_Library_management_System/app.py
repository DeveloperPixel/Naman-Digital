"""
Library Management System - Desktop Application
Version: 2.0
Features:
- Book management (add, edit, delete, search)
- User management (registration, deregistration, search)
- Borrowing system (issue, return, late fees)
- Advanced search functionality
- Late fee calculation
- Reports generation
- Data export/import
- Backup functionality
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import sqlite3
import json
import csv
import os
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from enum import Enum
from pathlib import Path

# Data Models
class BookStatus(Enum):
    AVAILABLE = "Available"
    BORROWED = "Borrowed"
    RESERVED = "Reserved"
    MAINTENANCE = "Maintenance"
    LOST = "Lost"
    DAMAGED = "Damaged"

class UserStatus(Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    SUSPENDED = "Suspended"
    EXPIRED = "Expired"

class MembershipType(Enum):
    REGULAR = "Regular"
    PREMIUM = "Premium"
    STUDENT = "Student"
    FACULTY = "Faculty"
    SENIOR = "Senior"

@dataclass
class Book:
    id: str
    title: str
    author: str
    isbn: str
    category: str
    status: BookStatus
    location: str
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    edition: Optional[str] = None
    pages: Optional[int] = None
    language: Optional[str] = "English"
    added_date: str = None
    last_updated: str = None
    notes: Optional[str] = None

@dataclass
class User:
    id: str
    name: str
    email: str
    phone: str
    address: str
    membership_date: str
    status: UserStatus
    membership_type: MembershipType = MembershipType.REGULAR
    expiry_date: Optional[str] = None
    borrowed_books: int = 0
    fine_amount: float = 0.0
    notes: Optional[str] = None

@dataclass
class BorrowRecord:
    id: str
    book_id: str
    user_id: str
    borrow_date: str
    due_date: str
    status: str = "Active"
    return_date: Optional[str] = None
    extended_date: Optional[str] = None
    late_fee: float = 0.0
    notes: Optional[str] = None

@dataclass
class Reservation:
    id: str
    book_id: str
    user_id: str
    reservation_date: str
    status: str = "Active"
    notes: Optional[str] = None

@dataclass
class Category:
    id: str
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None

class DatabaseManager:
    def __init__(self, db_file=None):
        if db_file is None:
            # Use the database in the same directory as the script
            self.db_file = os.path.join(os.path.dirname(__file__), 'library.db')
        else:
            self.db_file = db_file
        self._ensure_data_directory()
        self.setup_database()

    def _ensure_data_directory(self):
        """Ensure the data directory exists"""
        data_dir = os.path.dirname(self.db_file)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def setup_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()

        # Enable foreign key support
        c.execute("PRAGMA foreign_keys = ON")

        # Create Books table with additional fields
        c.execute('''CREATE TABLE IF NOT EXISTS books (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT UNIQUE NOT NULL,
            category TEXT,
            status TEXT NOT NULL,
            location TEXT,
            publisher TEXT,
            publication_year INTEGER,
            edition TEXT,
            pages INTEGER,
            language TEXT,
            added_date TEXT NOT NULL,
            last_updated TEXT NOT NULL,
            notes TEXT
        )''')

        # Create Users table with additional fields
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            address TEXT,
            membership_type TEXT DEFAULT 'Regular',
            membership_date TEXT NOT NULL,
            expiry_date TEXT,
            status TEXT NOT NULL,
            borrowed_books INTEGER DEFAULT 0,
            fine_amount REAL DEFAULT 0.0,
            notes TEXT
        )''')

        # Create BorrowRecords table with additional fields
        c.execute('''CREATE TABLE IF NOT EXISTS borrow_records (
            id TEXT PRIMARY KEY,
            book_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            borrow_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            return_date TEXT,
            extended_date TEXT,
            late_fee REAL DEFAULT 0.0,
            status TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY (book_id) REFERENCES books (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )''')

        # Create Reservations table
        c.execute('''CREATE TABLE IF NOT EXISTS reservations (
            id TEXT PRIMARY KEY,
            book_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            reservation_date TEXT NOT NULL,
            status TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY (book_id) REFERENCES books (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )''')

        # Create Categories table
        c.execute('''CREATE TABLE IF NOT EXISTS categories (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            parent_id TEXT,
            FOREIGN KEY (parent_id) REFERENCES categories (id)
        )''')

        conn.commit()
        conn.close()

    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database"""
        try:
            if os.path.exists(self.db_file):
                import shutil
                backup_file = f"{backup_path}/library_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                shutil.copy2(self.db_file, backup_file)
                return True
            return False
        except Exception as e:
            print(f"Backup error: {e}")
            return False

    def add_book(self, book: Book) -> bool:
        """Add a new book to the database"""
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            
            # Convert dataclass to dictionary and handle special types
            book_dict = asdict(book)
            book_dict['status'] = book.status.value
            
            # Prepare SQL statement dynamically
            fields = ', '.join(book_dict.keys())
            placeholders = ', '.join(['?' for _ in book_dict])
            sql = f'INSERT INTO books ({fields}) VALUES ({placeholders})'
            
            c.execute(sql, list(book_dict.values()))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding book: {e}")
            return False
        finally:
            conn.close()

    def add_user(self, user: User) -> bool:
        """Add a new user to the database"""
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute('''INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                     (user.id, user.name, user.email, user.phone, user.address,
                      user.membership_date, user.status, user.borrowed_books))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding user: {e}")
            return False
        finally:
            conn.close()

    def add_borrow_record(self, record: BorrowRecord) -> bool:
        """Add a new borrowing record"""
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute('''INSERT INTO borrow_records VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                     (record.id, record.book_id, record.user_id, record.borrow_date,
                      record.due_date, record.return_date, record.late_fee, record.status))
            # Update book status
            c.execute('''UPDATE books SET status = ? WHERE id = ?''',
                     (BookStatus.BORROWED.value, record.book_id))
            # Update user's borrowed books count
            c.execute('''UPDATE users SET borrowed_books = borrowed_books + 1 WHERE id = ?''',
                     (record.user_id,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding borrow record: {e}")
            return False
        finally:
            conn.close()

    def return_book(self, record_id: str, return_date: str, late_fee: float = 0.0) -> bool:
        """Process a book return"""
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            
            # Get the record details first
            c.execute('''SELECT book_id, user_id FROM borrow_records WHERE id = ?''', (record_id,))
            book_id, user_id = c.fetchone()
            
            # Update the borrow record
            c.execute('''UPDATE borrow_records 
                        SET return_date = ?, late_fee = ?, status = 'Returned'
                        WHERE id = ?''', (return_date, late_fee, record_id))
            
            # Update book status
            c.execute('''UPDATE books SET status = ? WHERE id = ?''',
                     (BookStatus.AVAILABLE.value, book_id))
            
            # Update user's borrowed books count
            c.execute('''UPDATE users SET borrowed_books = borrowed_books - 1 WHERE id = ?''',
                     (user_id,))
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error processing return: {e}")
            return False
        finally:
            conn.close()

class BookDialog:
    def __init__(self, parent, book=None):
        self.top = tk.Toplevel(parent)
        self.top.title("Add Book" if book is None else "Edit Book")
        self.book = book
        self.result = None
        self.create_widgets()
        if book:
            self.populate_fields()

    def create_widgets(self):
        # Create form fields
        fields = [
            ("Title:", "title"),
            ("Author:", "author"),
            ("ISBN:", "isbn"),
            ("Category:", "category"),
            ("Location:", "location")
        ]

        for i, (label, field) in enumerate(fields):
            tk.Label(self.top, text=label).grid(row=i, column=0, padx=5, pady=5)
            entry = tk.Entry(self.top)
            entry.grid(row=i, column=1, padx=5, pady=5)
            setattr(self, field, entry)

        # Status dropdown
        tk.Label(self.top, text="Status:").grid(row=len(fields), column=0, padx=5, pady=5)
        self.status = ttk.Combobox(self.top, values=[s.value for s in BookStatus])
        self.status.grid(row=len(fields), column=1, padx=5, pady=5)

        # Buttons
        btn_frame = tk.Frame(self.top)
        btn_frame.grid(row=len(fields)+1, column=0, columnspan=2, pady=10)
        
        tk.Button(btn_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=5)

    def populate_fields(self):
        if self.book:
            self.title.insert(0, self.book.title)
            self.author.insert(0, self.book.author)
            self.isbn.insert(0, self.book.isbn)
            self.category.insert(0, self.book.category)
            self.location.insert(0, self.book.location)
            self.status.set(self.book.status.value)

    def save(self):
        # Validate and save the data
        self.result = {
            'title': self.title.get(),
            'author': self.author.get(),
            'isbn': self.isbn.get(),
            'category': self.category.get(),
            'location': self.location.get(),
            'status': self.status.get()
        }
        self.top.destroy()

    def cancel(self):
        self.top.destroy()

class UserDialog:
    def __init__(self, parent, user=None):
        self.top = tk.Toplevel(parent)
        self.top.title("Add User" if user is None else "Edit User")
        self.user = user
        self.result = None
        self.create_widgets()
        if user:
            self.populate_fields()

    def create_widgets(self):
        # Create form fields
        fields = [
            ("Name:", "name"),
            ("Email:", "email"),
            ("Phone:", "phone"),
            ("Address:", "address")
        ]

        for i, (label, field) in enumerate(fields):
            tk.Label(self.top, text=label).grid(row=i, column=0, padx=5, pady=5)
            entry = tk.Entry(self.top)
            entry.grid(row=i, column=1, padx=5, pady=5)
            setattr(self, field, entry)

        # Status dropdown
        tk.Label(self.top, text="Status:").grid(row=len(fields), column=0, padx=5, pady=5)
        self.status = ttk.Combobox(self.top, values=["Active", "Inactive"])
        self.status.grid(row=len(fields), column=1, padx=5, pady=5)
        self.status.set("Active")

        # Buttons
        btn_frame = tk.Frame(self.top)
        btn_frame.grid(row=len(fields)+1, column=0, columnspan=2, pady=10)
        
        tk.Button(btn_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=5)

    def populate_fields(self):
        if self.user:
            self.name.insert(0, self.user.name)
            self.email.insert(0, self.user.email)
            self.phone.insert(0, self.user.phone)
            self.address.insert(0, self.user.address)
            self.status.set(self.user.status)

    def save(self):
        self.result = {
            'name': self.name.get(),
            'email': self.email.get(),
            'phone': self.phone.get(),
            'address': self.address.get(),
            'status': self.status.get()
        }
        self.top.destroy()

    def cancel(self):
        self.top.destroy()

class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.db = DatabaseManager()
        
        # Configure root window
        self.root.geometry("1200x800")
        self.root.configure(padx=10, pady=10)
        
        # Set theme and styles
        self.style = ttk.Style()
        self.style.theme_use('clam')  # or 'vista' on Windows
        
        # Configure styles
        self.style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'))
        self.style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'))
        
        # Initialize search variables
        self.book_search_var = tk.StringVar()
        self.user_search_var = tk.StringVar()
        self.book_search_var.trace('w', self.on_book_search_change)
        self.user_search_var.trace('w', self.on_user_search_change)
        
        self.create_widgets()
        self.create_menus()

    def create_menus(self):
        menubar = tk.Menu(self.root)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Backup Database", command=self.backup_database)
        file_menu.add_separator()
        file_menu.add_command(label="Export Data", command=self.export_data)
        file_menu.add_command(label="Import Data", command=self.import_data)
        file_menu.add_separator()
        file_menu.add_command(label="Settings", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Books Menu
        books_menu = tk.Menu(menubar, tearoff=0)
        books_menu.add_command(label="Add Book", command=self.add_book)
        books_menu.add_command(label="Edit Book", command=self.edit_book)
        books_menu.add_command(label="Delete Book", command=self.delete_book)
        books_menu.add_separator()
        books_menu.add_command(label="Advanced Search", command=self.advanced_book_search)
        books_menu.add_command(label="Manage Categories", command=self.manage_categories)
        books_menu.add_separator()
        books_menu.add_command(label="Book Reports", command=self.book_reports)
        menubar.add_cascade(label="Books", menu=books_menu)
        
        # Users Menu
        users_menu = tk.Menu(menubar, tearoff=0)
        users_menu.add_command(label="Add User", command=self.add_user)
        users_menu.add_command(label="Edit User", command=self.edit_user)
        users_menu.add_command(label="Delete User", command=self.delete_user)
        users_menu.add_separator()
        users_menu.add_command(label="Advanced Search", command=self.advanced_user_search)
        users_menu.add_command(label="Manage Memberships", command=self.manage_memberships)
        users_menu.add_separator()
        users_menu.add_command(label="User Reports", command=self.user_reports)
        menubar.add_cascade(label="Users", menu=users_menu)
        
        # Circulation Menu
        circ_menu = tk.Menu(menubar, tearoff=0)
        circ_menu.add_command(label="Issue Book", command=self.issue_book)
        circ_menu.add_command(label="Return Book", command=self.return_book)
        circ_menu.add_separator()
        circ_menu.add_command(label="Manage Reservations", command=self.manage_reservations)
        circ_menu.add_command(label="Manage Late Fees", command=self.manage_late_fees)
        circ_menu.add_separator()
        circ_menu.add_command(label="Circulation Reports", command=self.circulation_reports)
        menubar.add_cascade(label="Circulation", menu=circ_menu)
        
        # Reports Menu
        reports_menu = tk.Menu(menubar, tearoff=0)
        reports_menu.add_command(label="Daily Report", command=lambda: self.generate_report("daily"))
        reports_menu.add_command(label="Weekly Report", command=lambda: self.generate_report("weekly"))
        reports_menu.add_command(label="Monthly Report", command=lambda: self.generate_report("monthly"))
        reports_menu.add_separator()
        reports_menu.add_command(label="Custom Report", command=self.custom_report)
        menubar.add_cascade(label="Reports", menu=reports_menu)
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="User Guide", command=self.show_user_guide)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)

    def create_widgets(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both')
        
        # Books tab
        self.books_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.books_frame, text='Books')
        self.setup_books_tab()
        
        # Users tab
        self.users_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.users_frame, text='Users')
        self.setup_users_tab()
        
        # Circulation tab
        self.circ_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.circ_frame, text='Circulation')
        self.setup_circulation_tab()

    def setup_books_tab(self):
        # Search frame
        search_frame = ttk.Frame(self.books_frame)
        search_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side='left', padx=5)
        self.book_search = ttk.Entry(search_frame)
        self.book_search.pack(side='left', padx=5, fill='x', expand=True)
        
        # Books table
        columns = ('ID', 'Title', 'Author', 'ISBN', 'Status')
        self.books_tree = ttk.Treeview(self.books_frame, columns=columns, show='headings')
        
        for col in columns:
            self.books_tree.heading(col, text=col)
            self.books_tree.column(col, width=100)
        
        self.books_tree.pack(fill='both', expand=True, padx=5, pady=5)

    def setup_users_tab(self):
        # Search frame
        search_frame = ttk.Frame(self.users_frame)
        search_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side='left', padx=5)
        self.user_search = ttk.Entry(search_frame)
        self.user_search.pack(side='left', padx=5, fill='x', expand=True)
        
        # Users table
        columns = ('ID', 'Name', 'Email', 'Phone', 'Status')
        self.users_tree = ttk.Treeview(self.users_frame, columns=columns, show='headings')
        
        for col in columns:
            self.users_tree.heading(col, text=col)
            self.users_tree.column(col, width=100)
        
        self.users_tree.pack(fill='both', expand=True, padx=5, pady=5)

    def setup_circulation_tab(self):
        # Borrow frame
        borrow_frame = ttk.LabelFrame(self.circ_frame, text="Current Borrows")
        borrow_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        columns = ('ID', 'Book', 'User', 'Borrow Date', 'Due Date', 'Status')
        self.borrow_tree = ttk.Treeview(borrow_frame, columns=columns, show='headings')
        
        for col in columns:
            self.borrow_tree.heading(col, text=col)
            self.borrow_tree.column(col, width=100)
        
        self.borrow_tree.pack(fill='both', expand=True, padx=5, pady=5)

    def add_book(self):
        dialog = BookDialog(self.root)
        self.root.wait_window(dialog.top)
        if dialog.result:
            # Process the result and add to database
            book = Book(
                id=str(datetime.now().timestamp()),
                title=dialog.result['title'],
                author=dialog.result['author'],
                isbn=dialog.result['isbn'],
                category=dialog.result['category'],
                status=BookStatus(dialog.result['status']),
                location=dialog.result['location'],
                added_date=datetime.now().isoformat(),
                last_updated=datetime.now().isoformat()
            )
            if self.db.add_book(book):
                messagebox.showinfo("Success", "Book added successfully!")
                self.refresh_books()
            else:
                messagebox.showerror("Error", "Failed to add book")

    def add_user(self):
        dialog = UserDialog(self.root)
        self.root.wait_window(dialog.top)
        if dialog.result:
            # Process the result and add to database
            user = User(
                id=str(datetime.now().timestamp()),
                name=dialog.result['name'],
                email=dialog.result['email'],
                phone=dialog.result['phone'],
                address=dialog.result['address'],
                membership_date=datetime.now().isoformat(),
                status=dialog.result['status']
            )
            if self.db.add_user(user):
                messagebox.showinfo("Success", "User added successfully!")
                self.refresh_users()
            else:
                messagebox.showerror("Error", "Failed to add user")

    def issue_book(self):
        # This would open a dialog to select user and book
        pass

    def return_book(self):
        # This would open a dialog to process book return
        pass

    def search_books(self):
        # Implement book search functionality
        pass

    def backup_database(self):
        """Backup the database file"""
        backup_dir = filedialog.askdirectory(title="Select Backup Location")
        if backup_dir:
            if self.db.backup_database(backup_dir):
                messagebox.showinfo("Success", "Database backup created successfully!")
            else:
                messagebox.showerror("Error", "Failed to create database backup")

    def export_data(self):
        """Export data to CSV files"""
        export_dir = filedialog.askdirectory(title="Select Export Location")
        if export_dir:
            try:
                conn = sqlite3.connect(self.db.db_file)
                cursor = conn.cursor()
                
                # Export tables
                tables = ['books', 'users', 'borrow_records', 'reservations', 'categories']
                for table in tables:
                    cursor.execute(f"SELECT * FROM {table}")
                    rows = cursor.fetchall()
                    
                    # Get column names
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    # Write to CSV
                    with open(f"{export_dir}/{table}.csv", 'w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(columns)
                        writer.writerows(rows)
                
                messagebox.showinfo("Success", "Data exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data: {e}")
            finally:
                conn.close()

    def import_data(self):
        """Import data from CSV files"""
        import_dir = filedialog.askdirectory(title="Select Import Directory")
        if import_dir:
            try:
                conn = sqlite3.connect(self.db.db_file)
                cursor = conn.cursor()
                
                # Import tables
                tables = ['books', 'users', 'borrow_records', 'reservations', 'categories']
                for table in tables:
                    file_path = f"{import_dir}/{table}.csv"
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as f:
                            reader = csv.reader(f)
                            columns = next(reader)  # Get column names
                            
                            # Prepare SQL statement
                            placeholders = ','.join(['?' for _ in columns])
                            sql = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
                            
                            # Insert data
                            cursor.executemany(sql, reader)
                
                conn.commit()
                messagebox.showinfo("Success", "Data imported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import data: {e}")
            finally:
                conn.close()

    def show_settings(self):
        """Show settings dialog"""
        # TODO: Implement settings dialog
        pass

    def edit_book(self):
        """Edit selected book"""
        selected = self.books_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a book to edit")
            return
        
        book_id = self.books_tree.item(selected[0])['values'][0]
        # TODO: Get book details and show edit dialog
        pass

    def delete_book(self):
        """Delete selected book"""
        selected = self.books_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a book to delete")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this book?"):
            book_id = self.books_tree.item(selected[0])['values'][0]
            # TODO: Implement book deletion
            pass

    def advanced_book_search(self):
        """Show advanced book search dialog"""
        # TODO: Implement advanced search
        pass

    def manage_categories(self):
        """Show category management dialog"""
        # TODO: Implement category management
        pass

    def book_reports(self):
        """Show book reports dialog"""
        # TODO: Implement book reports
        pass

    def edit_user(self):
        """Edit selected user"""
        selected = self.users_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a user to edit")
            return
        
        user_id = self.users_tree.item(selected[0])['values'][0]
        # TODO: Get user details and show edit dialog
        pass

    def delete_user(self):
        """Delete selected user"""
        selected = self.users_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a user to delete")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this user?"):
            user_id = self.users_tree.item(selected[0])['values'][0]
            # TODO: Implement user deletion
            pass

    def advanced_user_search(self):
        """Show advanced user search dialog"""
        # TODO: Implement advanced search
        pass

    def manage_memberships(self):
        """Show membership management dialog"""
        # TODO: Implement membership management
        pass

    def user_reports(self):
        """Show user reports dialog"""
        # TODO: Implement user reports
        pass

    def manage_reservations(self):
        """Show reservation management dialog"""
        # TODO: Implement reservation management
        pass

    def manage_late_fees(self):
        """Show late fees management dialog"""
        # TODO: Implement late fees management
        pass

    def circulation_reports(self):
        """Show circulation reports dialog"""
        # TODO: Implement circulation reports
        pass

    def generate_report(self, report_type: str):
        """Generate specified report"""
        # TODO: Implement report generation
        pass

    def custom_report(self):
        """Show custom report dialog"""
        # TODO: Implement custom report
        pass

    def show_user_guide(self):
        """Show user guide"""
        # TODO: Implement user guide
        pass

    def show_about(self):
        """Show about dialog"""
        about_dialog = tk.Toplevel(self.root)
        about_dialog.title("About Library Management System")
        about_dialog.geometry("400x300")
        about_dialog.resizable(False, False)
        
        ttk.Label(about_dialog, text="Library Management System", style="Title.TLabel").pack(pady=20)
        ttk.Label(about_dialog, text="Version 2.0").pack()
        ttk.Label(about_dialog, text="© 2025 Your Organization").pack(pady=10)
        ttk.Label(about_dialog, text="A comprehensive solution for\nmanaging library operations", justify="center").pack(pady=10)
        
        ttk.Button(about_dialog, text="Close", command=about_dialog.destroy).pack(pady=20)

    def on_book_search_change(self, *args):
        """Handle book search input changes"""
        search_text = self.book_search_var.get().lower()
        for item in self.books_tree.get_children():
            values = [str(v).lower() for v in self.books_tree.item(item)['values']]
            if any(search_text in v for v in values):
                self.books_tree.reattach(item, '', 'end')
            else:
                self.books_tree.detach(item)

    def on_user_search_change(self, *args):
        """Handle user search input changes"""
        search_text = self.user_search_var.get().lower()
        for item in self.users_tree.get_children():
            values = [str(v).lower() for v in self.users_tree.item(item)['values']]
            if any(search_text in v for v in values):
                self.users_tree.reattach(item, '', 'end')
            else:
                self.users_tree.detach(item)

    def refresh_books(self):
        """Refresh the books treeview"""
        for item in self.books_tree.get_children():
            self.books_tree.delete(item)
            
        conn = sqlite3.connect(self.db.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, author, isbn, status FROM books")
        for row in cursor.fetchall():
            self.books_tree.insert('', 'end', values=row)
        conn.close()

    def refresh_users(self):
        """Refresh the users treeview"""
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
            
        conn = sqlite3.connect(self.db.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, phone, status FROM users")
        for row in cursor.fetchall():
            self.users_tree.insert('', 'end', values=row)
        conn.close()

    def refresh_all(self):
        """Refresh all data views"""
        self.refresh_books()
        self.refresh_users()
        self.refresh_circulation()

    def refresh_circulation(self):
        """Refresh the circulation treeview"""
        for item in self.borrow_tree.get_children():
            self.borrow_tree.delete(item)
            
        conn = sqlite3.connect(self.db.db_file)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT br.id, b.title, u.name, br.borrow_date, br.due_date, br.status
            FROM borrow_records br
            JOIN books b ON br.book_id = b.id
            JOIN users u ON br.user_id = u.id
            WHERE br.status = 'Active'
        """)
        for row in cursor.fetchall():
            self.borrow_tree.insert('', 'end', values=row)
        conn.close()

def main():
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
