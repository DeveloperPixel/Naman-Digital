from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this in production

# Database initialization
def init_db():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Create items table
    c.execute('''CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        quantity INTEGER NOT NULL DEFAULT 0,
        unit_price REAL NOT NULL,
        category TEXT,
        minimum_stock INTEGER DEFAULT 10,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Create transactions table
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        type TEXT CHECK(type IN ('in', 'out')) NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        total_amount REAL NOT NULL,
        reference_no TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (item_id) REFERENCES items (id)
    )''')
    
    conn.commit()
    conn.close()

# Database helper function
def get_db():
    conn = sqlite3.connect('inventory.db')
    conn.row_factory = sqlite3.Row
    return conn

# Login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        db = get_db()
        error = None
        
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not email:
            error = 'Email is required.'
        
        if error is None:
            try:
                db.execute(
                    'INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                    (username, generate_password_hash(password), email)
                )
                db.commit()
                flash('Registration successful! Please login.')
                return redirect(url_for('login'))
            except db.IntegrityError:
                error = f"User {username} or email {email} is already registered."
            finally:
                db.close()
                
        flash(error)
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        db.close()
        
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        
        flash(error)
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    
    # Get summary statistics
    stats = {}
    stats['total_items'] = db.execute('SELECT COUNT(*) FROM items').fetchone()[0]
    stats['total_value'] = db.execute(
        'SELECT SUM(quantity * unit_price) FROM items'
    ).fetchone()[0] or 0
    stats['low_stock'] = db.execute(
        'SELECT COUNT(*) FROM items WHERE quantity <= minimum_stock'
    ).fetchone()[0]
    
    # Get recent transactions
    recent_transactions = db.execute('''
        SELECT t.*, i.name as item_name 
        FROM transactions t
        JOIN items i ON t.item_id = i.id
        ORDER BY t.created_at DESC LIMIT 5
    ''').fetchall()
    
    # Get low stock items
    low_stock_items = db.execute('''
        SELECT * FROM items 
        WHERE quantity <= minimum_stock
        ORDER BY quantity ASC LIMIT 5
    ''').fetchall()
    
    db.close()
    return render_template('dashboard.html', 
                         stats=stats,
                         recent_transactions=recent_transactions,
                         low_stock_items=low_stock_items)

@app.route('/items')
@login_required
def items_list():
    db = get_db()
    items = db.execute('SELECT * FROM items ORDER BY name').fetchall()
    db.close()
    return render_template('items/list.html', items=items)

@app.route('/items/add', methods=['GET', 'POST'])
@login_required
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        quantity = int(request.form['quantity'])
        unit_price = float(request.form['unit_price'])
        category = request.form['category']
        minimum_stock = int(request.form['minimum_stock'])
        
        db = get_db()
        db.execute('''
            INSERT INTO items (name, description, quantity, unit_price, category, minimum_stock)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, description, quantity, unit_price, category, minimum_stock))
        
        # Record initial stock as transaction if quantity > 0
        if quantity > 0:
            item_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
            db.execute('''
                INSERT INTO transactions (item_id, type, quantity, unit_price, total_amount, notes)
                VALUES (?, 'in', ?, ?, ?, ?)
            ''', (item_id, quantity, unit_price, quantity * unit_price, 'Initial stock'))
        
        db.commit()
        db.close()
        flash('Item added successfully!')
        return redirect(url_for('items_list'))
    
    return render_template('items/add.html')

@app.route('/items/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_item(id):
    db = get_db()
    item = db.execute('SELECT * FROM items WHERE id = ?', (id,)).fetchone()
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']
        minimum_stock = int(request.form['minimum_stock'])
        
        db.execute('''
            UPDATE items 
            SET name=?, description=?, category=?, minimum_stock=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        ''', (name, description, category, minimum_stock, id))
        db.commit()
        db.close()
        
        flash('Item updated successfully!')
        return redirect(url_for('items_list'))
    
    db.close()
    return render_template('items/edit.html', item=item)

@app.route('/transactions')
@login_required
def transactions_list():
    db = get_db()
    transactions = db.execute('''
        SELECT t.*, i.name as item_name
        FROM transactions t
        JOIN items i ON t.item_id = i.id
        ORDER BY t.created_at DESC
    ''').fetchall()
    db.close()
    return render_template('transactions/list.html', transactions=transactions)

@app.route('/transactions/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    if request.method == 'POST':
        item_id = int(request.form['item_id'])
        trans_type = request.form['type']
        quantity = int(request.form['quantity'])
        unit_price = float(request.form['unit_price'])
        reference_no = request.form['reference_no']
        notes = request.form['notes']
        
        db = get_db()
        item = db.execute('SELECT quantity FROM items WHERE id = ?', (item_id,)).fetchone()
        
        if trans_type == 'out' and quantity > item['quantity']:
            flash('Error: Insufficient stock!')
            return redirect(url_for('add_transaction'))
        
        # Update item quantity
        new_quantity = item['quantity'] + quantity if trans_type == 'in' else item['quantity'] - quantity
        db.execute('UPDATE items SET quantity = ? WHERE id = ?', (new_quantity, item_id))
        
        # Add transaction record
        total_amount = quantity * unit_price
        db.execute('''
            INSERT INTO transactions (item_id, type, quantity, unit_price, total_amount, reference_no, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (item_id, trans_type, quantity, unit_price, total_amount, reference_no, notes))
        
        db.commit()
        db.close()
        flash('Transaction added successfully!')
        return redirect(url_for('transactions_list'))
    
    db = get_db()
    items = db.execute('SELECT id, name, quantity FROM items').fetchall()
    db.close()
    return render_template('transactions/add.html', items=items)

# Template filters
@app.template_filter('currency')
def currency_filter(value):
    return f"${value:,.2f}"

@app.template_filter('datetime')
def datetime_filter(value):
    if isinstance(value, str):
        value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    return value.strftime('%Y-%m-%d %H:%M')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
