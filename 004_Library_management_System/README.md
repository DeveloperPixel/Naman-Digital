# Library Management System

A desktop application built with Python and Tkinter for managing a library's books, users, and borrowing activities.

## Features

1. Book Management
   - Add new books with details (title, author, ISBN, etc.)
   - Track book status (available, borrowed, reserved, maintenance)
   - Search and filter books
   - View book history

2. User Management
   - User registration with contact details
   - Track borrowed books per user
   - User status management (active/inactive)
   - Search users

3. Circulation
   - Book issue and return processing
   - Automatic late fee calculation
   - Due date tracking
   - Borrowing history

4. Reports
   - Overdue books report
   - Popular books statistics
   - User activity report
   - Fine collection report

## Technical Details

- Built with Python 3.x and Tkinter
- Uses SQLite for data storage
- Object-oriented design with modular components
- Data validation and error handling
- Modern GUI with tabbed interface

## Installation

1. Ensure Python 3.x is installed
2. Clone the repository
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python app.py
   ```

## Database Schema

### Books Table
- id (Primary Key)
- title
- author
- isbn
- category
- status
- location
- added_date
- last_updated

### Users Table
- id (Primary Key)
- name
- email
- phone
- address
- membership_date
- status
- borrowed_books

### BorrowRecords Table
- id (Primary Key)
- book_id (Foreign Key)
- user_id (Foreign Key)
- borrow_date
- due_date
- return_date
- late_fee
- status

## Usage

1. Start the application
2. Use the top menu to access different functions:
   - File > Exit
   - Books > Add Book/Search Books
   - Users > Add User/Search Users
   - Circulation > Issue Book/Return Book

3. Main tabs:
   - Books: View and manage book inventory
   - Users: Manage user accounts
   - Circulation: Handle book borrowing/returns

## Configuration

The application uses the following default settings:
- Late fee rate: $0.50 per day
- Maximum borrowing period: 14 days
- Maximum books per user: 5
- Database file: library.db

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
