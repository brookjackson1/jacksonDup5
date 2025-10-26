from flask_login import UserMixin

class User(UserMixin):
    """User class for Flask-Login authentication"""

    def __init__(self, employee_id, email, first_name, last_name, role):
        self.id = employee_id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.role = role

    def __repr__(self):
        return f'<User {self.email}>'

    def get_id(self):
        """Return the user ID as a string (required by Flask-Login)"""
        return str(self.id)
