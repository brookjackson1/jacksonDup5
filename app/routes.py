from flask import render_template, request, redirect, url_for, flash, make_response
from flask_login import login_user, logout_user, login_required, current_user
from . import app
from .db_connect import get_db
from .models import User
import bcrypt
from functools import wraps

# Decorator to prevent caching (for logout and login pages)
def no_cache(view):
    @wraps(view)
    def no_cache_wrapper(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
    return no_cache_wrapper

@app.route('/')
@no_cache
def index():
    """Login page - redirect to dashboard if already logged in"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET'])
@no_cache
def login():
    """Login page route"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['POST'])
@no_cache
def login_post():
    """Handle login form submission"""
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    # Validate input
    if not email or not password:
        flash('Please provide both email and password.', 'error')
        return redirect(url_for('login'))

    # Get database connection
    db = get_db()
    if not db:
        flash('Database connection error. Please try again later.', 'error')
        return redirect(url_for('login'))

    # Check credentials
    cursor = db.cursor()
    cursor.execute("SELECT * FROM employees WHERE email = %s", (email,))
    employee = cursor.fetchone()
    cursor.close()

    # Verify user exists and password is correct
    if not employee:
        flash('Invalid email or password.', 'error')
        return redirect(url_for('login'))

    # Check password (compare with bcrypt hash)
    try:
        if bcrypt.checkpw(password.encode('utf-8'), employee['password'].encode('utf-8')):
            # Create user object and login
            user = User(
                employee['employee_id'],
                employee['email'],
                employee['first_name'],
                employee['last_name'],
                employee['role']
            )
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.first_name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
            return redirect(url_for('login'))
    except Exception as e:
        print(f"Password verification error: {e}")
        flash('Authentication error. Please try again.', 'error')
        return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
@no_cache
def dashboard():
    """Employee dashboard - main page after login"""
    # Get some statistics for the dashboard
    db = get_db()
    stats = {}

    if db:
        cursor = db.cursor()

        # Count total flights
        cursor.execute("SELECT COUNT(*) as count FROM flights")
        result = cursor.fetchone()
        stats['total_flights'] = result['count'] if result else 0

        # Count total customers
        cursor.execute("SELECT COUNT(*) as count FROM customers")
        result = cursor.fetchone()
        stats['total_customers'] = result['count'] if result else 0

        # Count total airports
        cursor.execute("SELECT COUNT(*) as count FROM airports")
        result = cursor.fetchone()
        stats['total_airports'] = result['count'] if result else 0

        # Count total bookings
        cursor.execute("SELECT COUNT(*) as count FROM bookings")
        result = cursor.fetchone()
        stats['total_bookings'] = result['count'] if result else 0

        cursor.close()

    return render_template('dashboard.html', user=current_user, stats=stats)

@app.route('/logout')
@login_required
@no_cache
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out successfully.', 'success')
    response = make_response(redirect(url_for('login')))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/flights')
@login_required
@no_cache
def flights():
    """View all flights"""
    db = get_db()
    flights = []

    if db:
        cursor = db.cursor()
        cursor.execute("""
            SELECT f.*,
                   a1.airport_code as departure_code, a1.city as departure_city,
                   a2.airport_code as arrival_code, a2.city as arrival_city
            FROM flights f
            JOIN airports a1 ON f.departure_airport_id = a1.airport_id
            JOIN airports a2 ON f.arrival_airport_id = a2.airport_id
            ORDER BY f.departure_time DESC
        """)
        flights = cursor.fetchall()
        cursor.close()

    return render_template('flights.html', flights=flights)

@app.route('/customers')
@login_required
@no_cache
def customers():
    """View all customers"""
    db = get_db()
    customers = []

    if db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM customers ORDER BY last_name, first_name")
        customers = cursor.fetchall()
        cursor.close()

    return render_template('customers.html', customers=customers)

@app.route('/airports')
@login_required
@no_cache
def airports():
    """View all airports/destinations"""
    db = get_db()
    airports = []

    if db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM airports ORDER BY country, city")
        airports = cursor.fetchall()
        cursor.close()

    return render_template('airports.html', airports=airports)

@app.route('/bookings')
@login_required
@no_cache
def bookings():
    """View all bookings"""
    db = get_db()
    bookings = []

    if db:
        cursor = db.cursor()
        cursor.execute("""
            SELECT b.*,
                   c.first_name, c.last_name, c.email,
                   f.flight_number,
                   a1.airport_code as departure_code,
                   a2.airport_code as arrival_code
            FROM bookings b
            JOIN customers c ON b.customer_id = c.customer_id
            JOIN flights f ON b.flight_id = f.flight_id
            JOIN airports a1 ON f.departure_airport_id = a1.airport_id
            JOIN airports a2 ON f.arrival_airport_id = a2.airport_id
            ORDER BY b.booking_date DESC
        """)
        bookings = cursor.fetchall()
        cursor.close()

    return render_template('bookings.html', bookings=bookings)

@app.route('/about')
def about():
    return render_template('about.html')
