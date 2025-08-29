from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this in production

def init_db():
    conn = sqlite3.connect('hotel.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        phone TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Create rooms table
    c.execute('''CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_number TEXT UNIQUE NOT NULL,
        room_type TEXT NOT NULL,
        capacity INTEGER NOT NULL,
        price_per_night REAL NOT NULL,
        amenities TEXT,
        status TEXT DEFAULT 'available' CHECK(status IN ('available', 'occupied', 'maintenance'))
    )''')
    
    # Create bookings table
    c.execute('''CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        room_id INTEGER NOT NULL,
        check_in_date DATE NOT NULL,
        check_out_date DATE NOT NULL,
        total_price REAL NOT NULL,
        status TEXT DEFAULT 'confirmed' CHECK(status IN ('confirmed', 'cancelled', 'completed')),
        guest_count INTEGER NOT NULL,
        special_requests TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (room_id) REFERENCES rooms (id)
    )''')
    
    # Insert some sample room types if they don't exist
    c.execute('SELECT COUNT(*) FROM rooms')
    if c.fetchone()[0] == 0:
        sample_rooms = [
            ('101', 'Standard Single', 1, 100.00, 'Wi-Fi, TV, AC'),
            ('102', 'Standard Single', 1, 100.00, 'Wi-Fi, TV, AC'),
            ('201', 'Deluxe Double', 2, 180.00, 'Wi-Fi, TV, AC, Mini Bar'),
            ('202', 'Deluxe Double', 2, 180.00, 'Wi-Fi, TV, AC, Mini Bar'),
            ('301', 'Suite', 4, 300.00, 'Wi-Fi, TV, AC, Mini Bar, Living Room'),
            ('302', 'Suite', 4, 300.00, 'Wi-Fi, TV, AC, Mini Bar, Living Room')
        ]
        c.executemany('INSERT INTO rooms (room_number, room_type, capacity, price_per_night, amenities) VALUES (?, ?, ?, ?, ?)',
                     sample_rooms)
    
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect('hotel.db')
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.template_filter('date')
def date_filter(value):
    if isinstance(value, str):
        return datetime.strptime(value, '%Y-%m-%d').strftime('%B %d, %Y')
    return value.strftime('%B %d, %Y')

@app.template_filter('currency')
def currency_filter(value):
    return f"${value:,.2f}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        full_name = request.form['full_name']
        phone = request.form['phone']
        
        db = get_db()
        try:
            db.execute('INSERT INTO users (username, password, email, full_name, phone) VALUES (?, ?, ?, ?, ?)',
                      [username, generate_password_hash(password), email, full_name, phone])
            db.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists!', 'error')
        finally:
            db.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', [username]).fetchone()
        db.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Welcome back!', 'success')
            return redirect(url_for('dashboard'))
        
        flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    # Get user's active bookings
    bookings = db.execute('''
        SELECT b.*, r.room_number, r.room_type, r.price_per_night
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        WHERE b.user_id = ? AND b.status = 'confirmed'
        ORDER BY b.check_in_date
    ''', [session['user_id']]).fetchall()
    db.close()
    
    return render_template('dashboard.html', bookings=bookings)

@app.route('/rooms')
def rooms():
    db = get_db()
    rooms = db.execute('SELECT * FROM rooms ORDER BY room_type, room_number').fetchall()
    db.close()
    return render_template('rooms.html', rooms=rooms)

@app.route('/book/<int:room_id>', methods=['GET', 'POST'])
@login_required
def book_room(room_id):
    db = get_db()
    room = db.execute('SELECT * FROM rooms WHERE id = ?', [room_id]).fetchone()
    
    if request.method == 'POST':
        check_in = request.form['check_in']
        check_out = request.form['check_out']
        guest_count = int(request.form['guest_count'])
        special_requests = request.form['special_requests']
        
        # Calculate total price
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d')
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d')
        nights = (check_out_date - check_in_date).days
        total_price = room['price_per_night'] * nights
        
        try:
            db.execute('''
                INSERT INTO bookings 
                (user_id, room_id, check_in_date, check_out_date, total_price, guest_count, special_requests)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', [session['user_id'], room_id, check_in, check_out, total_price, guest_count, special_requests])
            db.execute('UPDATE rooms SET status = ? WHERE id = ?', ['occupied', room_id])
            db.commit()
            flash('Booking confirmed!', 'success')
            return redirect(url_for('dashboard'))
        except sqlite3.Error as e:
            flash('Error making booking. Please try again.', 'error')
        finally:
            db.close()
    
    return render_template('book.html', room=room)

@app.route('/bookings')
@login_required
def bookings():
    db = get_db()
    bookings = db.execute('''
        SELECT b.*, r.room_number, r.room_type, u.full_name
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        JOIN users u ON b.user_id = u.id
        WHERE b.user_id = ?
        ORDER BY b.created_at DESC
    ''', [session['user_id']]).fetchall()
    db.close()
    return render_template('bookings.html', bookings=bookings)

@app.route('/cancel_booking/<int:booking_id>')
@login_required
def cancel_booking(booking_id):
    db = get_db()
    try:
        # Get the room_id first
        booking = db.execute('SELECT room_id FROM bookings WHERE id = ? AND user_id = ?', 
                           [booking_id, session['user_id']]).fetchone()
        if booking:
            db.execute('UPDATE bookings SET status = ? WHERE id = ?', ['cancelled', booking_id])
            db.execute('UPDATE rooms SET status = ? WHERE id = ?', ['available', booking['room_id']])
            db.commit()
            flash('Booking cancelled successfully!', 'success')
        else:
            flash('Booking not found!', 'error')
    except sqlite3.Error:
        flash('Error cancelling booking. Please try again.', 'error')
    finally:
        db.close()
    return redirect(url_for('bookings'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
