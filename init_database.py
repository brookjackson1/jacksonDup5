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
            print("Successfully connected to the database")
            return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

def execute_sql_file(connection, filename):
    """Execute SQL file to create tables"""
    try:
        cursor = connection.cursor()
        with open(filename, 'r') as file:
            sql_script = file.read()

        # Split by semicolons and execute each statement
        statements = sql_script.split(';')
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                cursor.execute(statement)

        connection.commit()
        print(f"Successfully executed {filename}")
        cursor.close()
    except Error as e:
        print(f"Error executing SQL file: {e}")

def insert_sample_data(connection):
    """Insert sample data into tables"""
    try:
        cursor = connection.cursor()

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

        connection.commit()
        print("Sample data inserted successfully!")
        cursor.close()

    except Error as e:
        print(f"Error inserting sample data: {e}")

def main():
    """Main function to initialize database"""
    print("=== Delta Airlines Database Initialization ===\n")

    # Create connection
    connection = create_connection()
    if not connection:
        return

    # Execute schema file
    print("\nCreating tables...")
    execute_sql_file(connection, 'database_schema.sql')

    # Insert sample data
    response = input("\nWould you like to insert sample data? (yes/no): ").strip().lower()
    if response in ['yes', 'y']:
        print("\nInserting sample data...")
        insert_sample_data(connection)
        print("\n=== Sample Employee Login Credentials ===")
        print("Email: john.smith@delta.com")
        print("Password: password123")
        print("Role: admin")

    # Close connection
    connection.close()
    print("\nDatabase initialization complete!")

if __name__ == "__main__":
    main()
