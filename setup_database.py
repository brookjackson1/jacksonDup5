import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import bcrypt

# Load environment variables
load_dotenv()

def create_connection():
    """Create database connection"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            port=int(os.getenv('DB_PORT', 3306))
        )
        if connection.is_connected():
            print("[OK] Successfully connected to the database")
            return connection
    except Error as e:
        print(f"[ERROR] Error connecting to database: {e}")
        return None

def create_tables(connection):
    """Create database tables"""
    try:
        cursor = connection.cursor()

        # Drop tables if they exist (in correct order due to foreign keys)
        print("\nDropping existing tables if any...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("DROP TABLE IF EXISTS bookings")
        cursor.execute("DROP TABLE IF EXISTS flights")
        cursor.execute("DROP TABLE IF EXISTS customers")
        cursor.execute("DROP TABLE IF EXISTS airports")
        cursor.execute("DROP TABLE IF EXISTS employees")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        print("Creating tables...")

        # Table 1: Employees
        cursor.execute("""
            CREATE TABLE employees (
                employee_id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(50) DEFAULT 'staff',
                hire_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("[OK] Created employees table")

        # Table 2: Airports
        cursor.execute("""
            CREATE TABLE airports (
                airport_id INT AUTO_INCREMENT PRIMARY KEY,
                airport_code VARCHAR(3) UNIQUE NOT NULL,
                airport_name VARCHAR(100) NOT NULL,
                city VARCHAR(50) NOT NULL,
                state VARCHAR(50),
                country VARCHAR(50) NOT NULL,
                timezone VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("[OK] Created airports table")

        # Table 3: Flights
        cursor.execute("""
            CREATE TABLE flights (
                flight_id INT AUTO_INCREMENT PRIMARY KEY,
                flight_number VARCHAR(10) NOT NULL,
                departure_airport_id INT NOT NULL,
                arrival_airport_id INT NOT NULL,
                departure_time DATETIME NOT NULL,
                arrival_time DATETIME NOT NULL,
                aircraft_type VARCHAR(50),
                status VARCHAR(20) DEFAULT 'Scheduled',
                gate VARCHAR(10),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (departure_airport_id) REFERENCES airports(airport_id),
                FOREIGN KEY (arrival_airport_id) REFERENCES airports(airport_id)
            )
        """)
        print("[OK] Created flights table")

        # Table 4: Customers
        cursor.execute("""
            CREATE TABLE customers (
                customer_id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                phone VARCHAR(20),
                frequent_flyer_number VARCHAR(20) UNIQUE,
                date_of_birth DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("[OK] Created customers table")

        # Table 5: Bookings
        cursor.execute("""
            CREATE TABLE bookings (
                booking_id INT AUTO_INCREMENT PRIMARY KEY,
                booking_reference VARCHAR(10) UNIQUE NOT NULL,
                customer_id INT NOT NULL,
                flight_id INT NOT NULL,
                booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                seat_number VARCHAR(10),
                booking_status VARCHAR(20) DEFAULT 'Confirmed',
                price DECIMAL(10, 2),
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
                FOREIGN KEY (flight_id) REFERENCES flights(flight_id)
            )
        """)
        print("[OK] Created bookings table")

        connection.commit()
        cursor.close()
        print("[OK] All tables created successfully!")

    except Error as e:
        print(f"[ERROR] Error creating tables: {e}")

def insert_sample_data(connection):
    """Insert sample data into tables"""
    try:
        cursor = connection.cursor()

        print("\nInserting sample data...")

        # Sample Employees (password: 'password123' hashed with bcrypt)
        hashed_pw = bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        employees_data = [
            ('John', 'Smith', 'john.smith@delta.com', hashed_pw, 'admin', '2020-01-15'),
            ('Sarah', 'Johnson', 'sarah.johnson@delta.com', hashed_pw, 'manager', '2019-06-20'),
            ('Michael', 'Williams', 'michael.williams@delta.com', hashed_pw, 'staff', '2021-03-10'),
            ('Emily', 'Brown', 'emily.brown@delta.com', hashed_pw, 'staff', '2022-08-05')
        ]

        cursor.executemany("""
            INSERT INTO employees (first_name, last_name, email, password, role, hire_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, employees_data)
        print("[OK] Inserted employee data")

        # Sample Airports
        airports_data = [
            ('ATL', 'Hartsfield-Jackson Atlanta International Airport', 'Atlanta', 'Georgia', 'USA', 'EST'),
            ('JFK', 'John F. Kennedy International Airport', 'New York', 'New York', 'USA', 'EST'),
            ('LAX', 'Los Angeles International Airport', 'Los Angeles', 'California', 'USA', 'PST'),
            ('ORD', 'O\'Hare International Airport', 'Chicago', 'Illinois', 'USA', 'CST'),
            ('DFW', 'Dallas/Fort Worth International Airport', 'Dallas', 'Texas', 'USA', 'CST'),
            ('DEN', 'Denver International Airport', 'Denver', 'Colorado', 'USA', 'MST'),
            ('MIA', 'Miami International Airport', 'Miami', 'Florida', 'USA', 'EST'),
            ('SEA', 'Seattle-Tacoma International Airport', 'Seattle', 'Washington', 'USA', 'PST')
        ]

        cursor.executemany("""
            INSERT INTO airports (airport_code, airport_name, city, state, country, timezone)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, airports_data)
        print("[OK] Inserted airport data")

        # Sample Customers
        customers_data = [
            ('James', 'Anderson', 'james.anderson@email.com', '555-0101', 'DL12345678', '1985-03-15'),
            ('Lisa', 'Martinez', 'lisa.martinez@email.com', '555-0102', 'DL23456789', '1990-07-22'),
            ('Robert', 'Taylor', 'robert.taylor@email.com', '555-0103', 'DL34567890', '1978-11-30'),
            ('Jennifer', 'Wilson', 'jennifer.wilson@email.com', '555-0104', 'DL45678901', '1995-05-18'),
            ('David', 'Moore', 'david.moore@email.com', '555-0105', 'DL56789012', '1982-09-25')
        ]

        cursor.executemany("""
            INSERT INTO customers (first_name, last_name, email, phone, frequent_flyer_number, date_of_birth)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, customers_data)
        print("[OK] Inserted customer data")

        # Sample Flights
        base_date = datetime.now() + timedelta(days=1)
        flights_data = [
            ('DL1001', 1, 2, base_date.replace(hour=8, minute=0), base_date.replace(hour=11, minute=30), 'Boeing 737', 'Scheduled', 'A12'),
            ('DL1002', 2, 1, base_date.replace(hour=13, minute=0), base_date.replace(hour=16, minute=30), 'Boeing 737', 'Scheduled', 'B24'),
            ('DL2001', 1, 3, base_date.replace(hour=9, minute=15), base_date.replace(hour=11, minute=45), 'Airbus A320', 'Scheduled', 'C15'),
            ('DL2002', 3, 1, base_date.replace(hour=14, minute=30), base_date.replace(hour=22, minute=45), 'Airbus A320', 'Scheduled', 'D08'),
            ('DL3001', 1, 4, base_date.replace(hour=7, minute=0), base_date.replace(hour=9, minute=15), 'Boeing 757', 'Scheduled', 'A05'),
            ('DL3002', 4, 1, base_date.replace(hour=18, minute=45), base_date.replace(hour=21, minute=0), 'Boeing 757', 'Scheduled', 'B18'),
            ('DL4001', 1, 7, base_date.replace(hour=10, minute=30), base_date.replace(hour=13, minute=15), 'Airbus A330', 'Scheduled', 'E22'),
            ('DL5001', 5, 6, base_date.replace(hour=15, minute=0), base_date.replace(hour=17, minute=30), 'Boeing 737', 'Scheduled', 'F10')
        ]

        cursor.executemany("""
            INSERT INTO flights (flight_number, departure_airport_id, arrival_airport_id,
                               departure_time, arrival_time, aircraft_type, status, gate)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, flights_data)
        print("[OK] Inserted flight data")

        # Sample Bookings
        bookings_data = [
            ('ABC123', 1, 1, '12A', 'Confirmed', 299.99),
            ('DEF456', 2, 3, '14C', 'Confirmed', 450.00),
            ('GHI789', 3, 5, '22F', 'Confirmed', 199.99),
            ('JKL012', 4, 7, '8B', 'Confirmed', 325.50),
            ('MNO345', 5, 2, '15D', 'Confirmed', 289.00),
            ('PQR678', 1, 4, '10A', 'Confirmed', 399.99)
        ]

        cursor.executemany("""
            INSERT INTO bookings (booking_reference, customer_id, flight_id, seat_number, booking_status, price)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, bookings_data)
        print("[OK] Inserted booking data")

        connection.commit()
        cursor.close()
        print("\n[OK] All sample data inserted successfully!")

    except Error as e:
        print(f"[ERROR] Error inserting sample data: {e}")

def main():
    """Main function to initialize database"""
    print("=" * 50)
    print("Delta Airlines Database Setup")
    print("=" * 50)

    # Create connection
    connection = create_connection()
    if not connection:
        return

    # Create tables
    create_tables(connection)

    # Insert sample data
    insert_sample_data(connection)

    # Close connection
    connection.close()

    print("\n" + "=" * 50)
    print("Database setup complete!")
    print("=" * 50)
    print("\nTest Login Credentials:")
    print("  Email:    john.smith@delta.com")
    print("  Password: password123")
    print("=" * 50)

if __name__ == "__main__":
    main()
