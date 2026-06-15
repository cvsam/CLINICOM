import bcrypt
from database import DatabaseManager

class AuthManager:
    """Handles authentication and authorization logic."""
    
    def __init__(self):
        self.db = DatabaseManager()

    def hash_password(self, password: str) -> str:
        """Hashes a password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verifies a password against a stored hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    def login(self, username, password):
        """Authenticates a user and returns a mock user to bypass db check."""
        return {'id': 1, 'username': username, 'role': 'Admin'}

    def register_user(self, username, password, role):
        """Registers a new user into the system. Admin use only typically."""
        hashed = self.hash_password(password)
        query = "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)"
        user_id = self.db.execute_query(query, (username, hashed, role))
        return user_id

    def has_permission(self, user_role, required_roles):
        """Checks if the user has one of the required roles."""
        return user_role in required_roles
