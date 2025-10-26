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
    """View all active flights"""
    db = get_db()
    flights = []
    airports = []

    if db:
        cursor = db.cursor()

        # Get all active flights
        cursor.execute("""
            SELECT f.*,
                   a1.airport_code as departure_code, a1.city as departure_city,
                   a2.airport_code as arrival_code, a2.city as arrival_city
            FROM flights f
            JOIN airports a1 ON f.departure_airport_id = a1.airport_id
            JOIN airports a2 ON f.arrival_airport_id = a2.airport_id
            WHERE f.is_archived = FALSE
            ORDER BY f.departure_time DESC
        """)
        flights = cursor.fetchall()

        # Get all airports for dropdown
        cursor.execute("SELECT * FROM airports WHERE is_archived = FALSE ORDER BY airport_code")
        airports = cursor.fetchall()

        cursor.close()

    return render_template('flights.html', flights=flights, airports=airports)

@app.route('/flights/add', methods=['POST'])
@login_required
def add_flight():
    """Add a new flight"""
    db = get_db()

    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO flights (flight_number, departure_airport_id, arrival_airport_id,
                               departure_time, arrival_time, aircraft_type, status, gate)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            request.form['flight_number'],
            request.form['departure_airport_id'],
            request.form['arrival_airport_id'],
            request.form['departure_time'],
            request.form['arrival_time'],
            request.form['aircraft_type'],
            request.form['status'],
            request.form['gate']
        ))
        db.commit()
        cursor.close()
        flash('Flight added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding flight: {str(e)}', 'error')

    return redirect(url_for('flights'))

@app.route('/flights/edit/<int:flight_id>', methods=['POST'])
@login_required
def edit_flight(flight_id):
    """Edit an existing flight"""
    db = get_db()

    try:
        cursor = db.cursor()
        cursor.execute("""
            UPDATE flights
            SET flight_number = %s, departure_airport_id = %s, arrival_airport_id = %s,
                departure_time = %s, arrival_time = %s, aircraft_type = %s,
                status = %s, gate = %s
            WHERE flight_id = %s AND is_archived = FALSE
        """, (
            request.form['flight_number'],
            request.form['departure_airport_id'],
            request.form['arrival_airport_id'],
            request.form['departure_time'],
            request.form['arrival_time'],
            request.form['aircraft_type'],
            request.form['status'],
            request.form['gate'],
            flight_id
        ))
        db.commit()
        cursor.close()
        flash('Flight updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating flight: {str(e)}', 'error')

    return redirect(url_for('flights'))

@app.route('/flights/delete/<int:flight_id>', methods=['POST'])
@login_required
def delete_flight(flight_id):
    """Archive a flight (soft delete)"""
    db = get_db()

    try:
        cursor = db.cursor()
        cursor.execute("""
            UPDATE flights
            SET is_archived = TRUE, archived_at = NOW(), archived_by = %s
            WHERE flight_id = %s
        """, (current_user.id, flight_id))
        db.commit()
        cursor.close()
        flash('Flight archived successfully!', 'success')
    except Exception as e:
        flash(f'Error archiving flight: {str(e)}', 'error')

    return redirect(url_for('flights'))

@app.route('/customers')
@login_required
@no_cache
def customers():
    """View all active customers"""
    db = get_db()
    customers = []

    if db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM customers WHERE is_archived = FALSE ORDER BY last_name, first_name")
        customers = cursor.fetchall()
        cursor.close()

    return render_template('customers.html', customers=customers)

@app.route('/customers/add', methods=['POST'])
@login_required
def add_customer():
    """Add a new customer"""
    db = get_db()

    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO customers (first_name, last_name, email, phone,
                                 frequent_flyer_number, date_of_birth)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            request.form['first_name'],
            request.form['last_name'],
            request.form['email'],
            request.form['phone'],
            request.form['frequent_flyer_number'],
            request.form['date_of_birth'] if request.form['date_of_birth'] else None
        ))
        db.commit()
        cursor.close()
        flash('Customer added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding customer: {str(e)}', 'error')

    return redirect(url_for('customers'))

@app.route('/customers/edit/<int:customer_id>', methods=['POST'])
@login_required
def edit_customer(customer_id):
    """Edit an existing customer"""
    db = get_db()

    try:
        cursor = db.cursor()
        cursor.execute("""
            UPDATE customers
            SET first_name = %s, last_name = %s, email = %s, phone = %s,
                frequent_flyer_number = %s, date_of_birth = %s
            WHERE customer_id = %s AND is_archived = FALSE
        """, (
            request.form['first_name'],
            request.form['last_name'],
            request.form['email'],
            request.form['phone'],
            request.form['frequent_flyer_number'],
            request.form['date_of_birth'] if request.form['date_of_birth'] else None,
            customer_id
        ))
        db.commit()
        cursor.close()
        flash('Customer updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating customer: {str(e)}', 'error')

    return redirect(url_for('customers'))

@app.route('/customers/delete/<int:customer_id>', methods=['POST'])
@login_required
def delete_customer(customer_id):
    """Archive a customer (soft delete)"""
    db = get_db()

    try:
        cursor = db.cursor()
        cursor.execute("""
            UPDATE customers
            SET is_archived = TRUE, archived_at = NOW(), archived_by = %s
            WHERE customer_id = %s
        """, (current_user.id, customer_id))
        db.commit()
        cursor.close()
        flash('Customer archived successfully!', 'success')
    except Exception as e:
        flash(f'Error archiving customer: {str(e)}', 'error')

    return redirect(url_for('customers'))

@app.route('/airports')
@login_required
@no_cache
def airports():
    """View all active airports/destinations"""
    db = get_db()
    airports = []

    if db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM airports WHERE is_archived = FALSE ORDER BY country, city")
        airports = cursor.fetchall()
        cursor.close()

    return render_template('airports.html', airports=airports)

@app.route('/airports/add', methods=['POST'])
@login_required
def add_airport():
    """Add a new airport"""
    db = get_db()

    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO airports (airport_code, airport_name, city, state, country, timezone)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            request.form['airport_code'],
            request.form['airport_name'],
            request.form['city'],
            request.form['state'] if request.form['state'] else None,
            request.form['country'],
            request.form['timezone']
        ))
        db.commit()
        cursor.close()
        flash('Airport added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding airport: {str(e)}', 'error')

    return redirect(url_for('airports'))

@app.route('/airports/edit/<int:airport_id>', methods=['POST'])
@login_required
def edit_airport(airport_id):
    """Edit an existing airport"""
    db = get_db()

    try:
        cursor = db.cursor()
        cursor.execute("""
            UPDATE airports
            SET airport_code = %s, airport_name = %s, city = %s,
                state = %s, country = %s, timezone = %s
            WHERE airport_id = %s AND is_archived = FALSE
        """, (
            request.form['airport_code'],
            request.form['airport_name'],
            request.form['city'],
            request.form['state'] if request.form['state'] else None,
            request.form['country'],
            request.form['timezone'],
            airport_id
        ))
        db.commit()
        cursor.close()
        flash('Airport updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating airport: {str(e)}', 'error')

    return redirect(url_for('airports'))

@app.route('/airports/delete/<int:airport_id>', methods=['POST'])
@login_required
def delete_airport(airport_id):
    """Archive an airport (soft delete)"""
    db = get_db()

    try:
        cursor = db.cursor()
        cursor.execute("""
            UPDATE airports
            SET is_archived = TRUE, archived_at = NOW(), archived_by = %s
            WHERE airport_id = %s
        """, (current_user.id, airport_id))
        db.commit()
        cursor.close()
        flash('Airport archived successfully!', 'success')
    except Exception as e:
        flash(f'Error archiving airport: {str(e)}', 'error')

    return redirect(url_for('airports'))

@app.route('/bookings')
@login_required
@no_cache
def bookings():
    """View all active bookings"""
    db = get_db()
    bookings = []
    customers = []
    flights = []

    if db:
        cursor = db.cursor()

        # Get all active bookings
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
            WHERE b.is_archived = FALSE
            ORDER BY b.booking_date DESC
        """)
        bookings = cursor.fetchall()

        # Get all customers for dropdown
        cursor.execute("SELECT * FROM customers WHERE is_archived = FALSE ORDER BY last_name, first_name")
        customers = cursor.fetchall()

        # Get all flights for dropdown
        cursor.execute("""
            SELECT f.*,
                   a1.airport_code as departure_code,
                   a2.airport_code as arrival_code
            FROM flights f
            JOIN airports a1 ON f.departure_airport_id = a1.airport_id
            JOIN airports a2 ON f.arrival_airport_id = a2.airport_id
            WHERE f.is_archived = FALSE
            ORDER BY f.departure_time DESC
        """)
        flights = cursor.fetchall()

        cursor.close()

    return render_template('bookings.html', bookings=bookings, customers=customers, flights=flights)

@app.route('/bookings/add', methods=['POST'])
@login_required
def add_booking():
    """Add a new booking"""
    db = get_db()

    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO bookings (booking_reference, customer_id, flight_id,
                                seat_number, booking_status, price)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            request.form['booking_reference'],
            request.form['customer_id'],
            request.form['flight_id'],
            request.form['seat_number'],
            request.form['booking_status'],
            request.form['price']
        ))
        db.commit()
        cursor.close()
        flash('Booking added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding booking: {str(e)}', 'error')

    return redirect(url_for('bookings'))

@app.route('/bookings/edit/<int:booking_id>', methods=['POST'])
@login_required
def edit_booking(booking_id):
    """Edit an existing booking"""
    db = get_db()

    try:
        cursor = db.cursor()
        cursor.execute("""
            UPDATE bookings
            SET booking_reference = %s, customer_id = %s, flight_id = %s,
                seat_number = %s, booking_status = %s, price = %s
            WHERE booking_id = %s AND is_archived = FALSE
        """, (
            request.form['booking_reference'],
            request.form['customer_id'],
            request.form['flight_id'],
            request.form['seat_number'],
            request.form['booking_status'],
            request.form['price'],
            booking_id
        ))
        db.commit()
        cursor.close()
        flash('Booking updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating booking: {str(e)}', 'error')

    return redirect(url_for('bookings'))

@app.route('/bookings/delete/<int:booking_id>', methods=['POST'])
@login_required
def delete_booking(booking_id):
    """Archive a booking (soft delete)"""
    db = get_db()

    try:
        cursor = db.cursor()
        cursor.execute("""
            UPDATE bookings
            SET is_archived = TRUE, archived_at = NOW(), archived_by = %s
            WHERE booking_id = %s
        """, (current_user.id, booking_id))
        db.commit()
        cursor.close()
        flash('Booking archived successfully!', 'success')
    except Exception as e:
        flash(f'Error archiving booking: {str(e)}', 'error')

    return redirect(url_for('bookings'))

# Archive Routes
@app.route('/archive')
@login_required
@no_cache
def archive():
    """View all archived items"""
    db = get_db()
    stats = {
        'flights': 0,
        'customers': 0,
        'airports': 0,
        'bookings': 0
    }

    if db:
        cursor = db.cursor()

        # Count archived items
        cursor.execute("SELECT COUNT(*) as count FROM flights WHERE is_archived = TRUE")
        result = cursor.fetchone()
        stats['flights'] = result['count'] if result else 0

        cursor.execute("SELECT COUNT(*) as count FROM customers WHERE is_archived = TRUE")
        result = cursor.fetchone()
        stats['customers'] = result['count'] if result else 0

        cursor.execute("SELECT COUNT(*) as count FROM airports WHERE is_archived = TRUE")
        result = cursor.fetchone()
        stats['airports'] = result['count'] if result else 0

        cursor.execute("SELECT COUNT(*) as count FROM bookings WHERE is_archived = TRUE")
        result = cursor.fetchone()
        stats['bookings'] = result['count'] if result else 0

        cursor.close()

    return render_template('archive.html', stats=stats)

@app.route('/archive/flights')
@login_required
@no_cache
def archive_flights():
    """View archived flights"""
    db = get_db()
    flights = []
    airports = []

    if db:
        cursor = db.cursor()
        cursor.execute("""
            SELECT f.*,
                   a1.airport_code as departure_code, a1.city as departure_city,
                   a2.airport_code as arrival_code, a2.city as arrival_city,
                   e.first_name as archived_by_name
            FROM flights f
            JOIN airports a1 ON f.departure_airport_id = a1.airport_id
            JOIN airports a2 ON f.arrival_airport_id = a2.airport_id
            LEFT JOIN employees e ON f.archived_by = e.employee_id
            WHERE f.is_archived = TRUE
            ORDER BY f.archived_at DESC
        """)
        flights = cursor.fetchall()
        cursor.close()

    return render_template('archive_flights.html', flights=flights)

@app.route('/archive/customers')
@login_required
@no_cache
def archive_customers():
    """View archived customers"""
    db = get_db()
    customers = []

    if db:
        cursor = db.cursor()
        cursor.execute("""
            SELECT c.*, e.first_name as archived_by_name
            FROM customers c
            LEFT JOIN employees e ON c.archived_by = e.employee_id
            WHERE c.is_archived = TRUE
            ORDER BY c.archived_at DESC
        """)
        customers = cursor.fetchall()
        cursor.close()

    return render_template('archive_customers.html', customers=customers)

@app.route('/archive/airports')
@login_required
@no_cache
def archive_airports():
    """View archived airports"""
    db = get_db()
    airports = []

    if db:
        cursor = db.cursor()
        cursor.execute("""
            SELECT a.*, e.first_name as archived_by_name
            FROM airports a
            LEFT JOIN employees e ON a.archived_by = e.employee_id
            WHERE a.is_archived = TRUE
            ORDER BY a.archived_at DESC
        """)
        airports = cursor.fetchall()
        cursor.close()

    return render_template('archive_airports.html', airports=airports)

@app.route('/archive/bookings')
@login_required
@no_cache
def archive_bookings():
    """View archived bookings"""
    db = get_db()
    bookings = []

    if db:
        cursor = db.cursor()
        cursor.execute("""
            SELECT b.*,
                   c.first_name, c.last_name, c.email,
                   f.flight_number,
                   a1.airport_code as departure_code,
                   a2.airport_code as arrival_code,
                   e.first_name as archived_by_name
            FROM bookings b
            JOIN customers c ON b.customer_id = c.customer_id
            JOIN flights f ON b.flight_id = f.flight_id
            JOIN airports a1 ON f.departure_airport_id = a1.airport_id
            JOIN airports a2 ON f.arrival_airport_id = a2.airport_id
            LEFT JOIN employees e ON b.archived_by = e.employee_id
            WHERE b.is_archived = TRUE
            ORDER BY b.archived_at DESC
        """)
        bookings = cursor.fetchall()
        cursor.close()

    return render_template('archive_bookings.html', bookings=bookings)

# Restore Routes
@app.route('/restore/flight/<int:flight_id>', methods=['POST'])
@login_required
def restore_flight(flight_id):
    """Restore an archived flight"""
    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute("""
            UPDATE flights
            SET is_archived = FALSE, archived_at = NULL, archived_by = NULL
            WHERE flight_id = %s
        """, (flight_id,))
        db.commit()
        cursor.close()
        flash('Flight restored successfully!', 'success')
    except Exception as e:
        flash(f'Error restoring flight: {str(e)}', 'error')
    return redirect(url_for('archive_flights'))

@app.route('/restore/customer/<int:customer_id>', methods=['POST'])
@login_required
def restore_customer(customer_id):
    """Restore an archived customer"""
    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute("""
            UPDATE customers
            SET is_archived = FALSE, archived_at = NULL, archived_by = NULL
            WHERE customer_id = %s
        """, (customer_id,))
        db.commit()
        cursor.close()
        flash('Customer restored successfully!', 'success')
    except Exception as e:
        flash(f'Error restoring customer: {str(e)}', 'error')
    return redirect(url_for('archive_customers'))

@app.route('/restore/airport/<int:airport_id>', methods=['POST'])
@login_required
def restore_airport(airport_id):
    """Restore an archived airport"""
    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute("""
            UPDATE airports
            SET is_archived = FALSE, archived_at = NULL, archived_by = NULL
            WHERE airport_id = %s
        """, (airport_id,))
        db.commit()
        cursor.close()
        flash('Airport restored successfully!', 'success')
    except Exception as e:
        flash(f'Error restoring airport: {str(e)}', 'error')
    return redirect(url_for('archive_airports'))

@app.route('/restore/booking/<int:booking_id>', methods=['POST'])
@login_required
def restore_booking(booking_id):
    """Restore an archived booking"""
    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute("""
            UPDATE bookings
            SET is_archived = FALSE, archived_at = NULL, archived_by = NULL
            WHERE booking_id = %s
        """, (booking_id,))
        db.commit()
        cursor.close()
        flash('Booking restored successfully!', 'success')
    except Exception as e:
        flash(f'Error restoring booking: {str(e)}', 'error')
    return redirect(url_for('archive_bookings'))

@app.route('/about')
def about():
    return render_template('about.html')
