from flask import Flask, g
from flask_login import LoginManager
from .app_factory import create_app
from .db_connect import close_db, get_db
from .models import User

app = create_app()
app.secret_key = 'your-secret-key-change-this-in-production'  # Replace with an environment variable

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'error'

@login_manager.user_loader
def load_user(user_id):
    """Load user from database for Flask-Login"""
    db = get_db()
    if db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM employees WHERE employee_id = %s", (user_id,))
        employee = cursor.fetchone()
        cursor.close()

        if employee:
            return User(
                employee['employee_id'],
                employee['email'],
                employee['first_name'],
                employee['last_name'],
                employee['role']
            )
    return None

# Register Blueprints
from . import routes

@app.before_request
def before_request():
    g.db = get_db()
    if g.db is None:
        print("Warning: Database connection unavailable. Some features may not work.")

# Setup database connection teardown
@app.teardown_appcontext
def teardown_db(exception=None):
    close_db(exception)