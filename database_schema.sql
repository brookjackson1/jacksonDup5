-- Delta Airlines Employee Portal Database Schema
-- 5 Tables: employees, airports, flights, customers, bookings

-- Table 1: Employees (for login and authentication)
CREATE TABLE IF NOT EXISTS employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'staff',
    hire_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 2: Airports (destinations)
CREATE TABLE IF NOT EXISTS airports (
    airport_id INT AUTO_INCREMENT PRIMARY KEY,
    airport_code VARCHAR(3) UNIQUE NOT NULL,
    airport_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    state VARCHAR(50),
    country VARCHAR(50) NOT NULL,
    timezone VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 3: Flights
CREATE TABLE IF NOT EXISTS flights (
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
);

-- Table 4: Customers (passengers)
CREATE TABLE IF NOT EXISTS customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    frequent_flyer_number VARCHAR(20) UNIQUE,
    date_of_birth DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 5: Bookings (flight reservations)
CREATE TABLE IF NOT EXISTS bookings (
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
);

-- Create indexes for better query performance
CREATE INDEX idx_flight_number ON flights(flight_number);
CREATE INDEX idx_employee_email ON employees(email);
CREATE INDEX idx_customer_email ON customers(email);
CREATE INDEX idx_booking_reference ON bookings(booking_reference);
CREATE INDEX idx_departure_time ON flights(departure_time);
