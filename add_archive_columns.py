import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

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

def add_archive_columns(connection):
    """Add is_archived column to all tables"""
    try:
        cursor = connection.cursor()

        tables = ['employees', 'airports', 'flights', 'customers', 'bookings']

        print("\nAdding is_archived columns to tables...")

        for table in tables:
            # Check if column already exists
            cursor.execute(f"""
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = '{os.getenv('DB_NAME')}'
                AND TABLE_NAME = '{table}'
                AND COLUMN_NAME = 'is_archived'
            """)

            result = cursor.fetchone()

            if result[0] == 0:
                # Column doesn't exist, add it
                cursor.execute(f"""
                    ALTER TABLE {table}
                    ADD COLUMN is_archived BOOLEAN DEFAULT FALSE,
                    ADD COLUMN archived_at TIMESTAMP NULL,
                    ADD COLUMN archived_by INT NULL
                """)
                print(f"[OK] Added archive columns to {table}")
            else:
                print(f"[SKIP] Archive columns already exist in {table}")

        connection.commit()
        cursor.close()
        print("\n[OK] Database migration completed successfully!")

    except Error as e:
        print(f"[ERROR] Error during migration: {e}")

def main():
    """Main function to run migration"""
    print("=" * 50)
    print("Delta Airlines - Add Archive Columns Migration")
    print("=" * 50)

    # Create connection
    connection = create_connection()
    if not connection:
        return

    # Add archive columns
    add_archive_columns(connection)

    # Close connection
    connection.close()

    print("\n" + "=" * 50)
    print("Migration complete!")
    print("=" * 50)

if __name__ == "__main__":
    main()
