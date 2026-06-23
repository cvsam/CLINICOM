"""
auth.py — Authentication and Authorization Module for CLINICOM
============================================================
Handles user login, registration, and role-based access control.

Features:
    - Secure password hashing with bcrypt
    - Encapsulated validation methods
    - Session management utilities
"""

import bcrypt

from database import get_session
from models import User


class AuthManager:
    """Handles authentication and authorization logic using SQLAlchemy.
    
    Demonstrates ENCAPSULATION by using private helper methods
    to validate inputs and handle password cryptography internally.
    """

    def _validate_credentials(self, username, password):
        """Private helper to validate credential formats (ENCAPSULATION)."""
        if not username or not password:
            return False
        if len(username.strip()) < 3 or len(password) < 6:
            return False
        return True

    def _hash_password(self, password: str) -> str:
        """Private helper: Hashes a password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """Private helper: Verifies a password against a stored bcrypt hash."""
        return bcrypt.checkpw(
            password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    def login(self, username, password):
        """Authenticate a user against the database.
        
        Args:
            username: The user's login name.
            password: The plain-text password.
            
        Returns:
            A dict with user info on success, or None on failure.
        """
        if not self._validate_credentials(username, password):
            print("[Auth Error] Invalid username or password format.")
            return None

        try:
            with get_session() as session:
                user = (
                    session.query(User)
                    .filter(User.username == username.strip())
                    .first()
                )
                if user and self._verify_password(password, user.password_hash):
                    return {
                        "id": user.id,
                        "username": user.username,
                        "role": user.role,
                    }
        except Exception as e:
            print(f"[DB Error] login: {e}")
        
        return None

    def register_user(self, username, password, role):
        """Register a new system user.
        
        Args:
            username: Login name.
            password: Plain-text password (will be hashed).
            role:     User role (Admin, Doctor, Receptionist).
            
        Returns:
            The new user's ID or None on failure.
        """
        if not self._validate_credentials(username, password):
            print("[Auth Error] Username (min 3 chars) and password (min 6 chars) required.")
            return None
            
        if role not in ("Admin", "Doctor", "Receptionist"):
            print("[Auth Error] Role must be Admin, Doctor, or Receptionist.")
            return None

        try:
            with get_session() as session:
                # Check if username exists
                existing = session.query(User).filter(User.username == username.strip()).first()
                if existing:
                    print("[Auth Error] Username already exists.")
                    return None
                    
                hashed = self._hash_password(password)
                user = User(
                    username=username.strip(),
                    password_hash=hashed,
                    role=role,
                )
                session.add(user)
                session.flush()
                return user.id
        except Exception as e:
            print(f"[DB Error] register_user: {e}")
            return None

    def has_permission(self, user_role, required_roles):
        """Checks if the user has one of the required roles for an action."""
        return user_role in required_roles

    def get_all_users(self):
        """Get all registered users."""
        try:
            with get_session() as session:
                users = session.query(User).all()
                return [{"id": u.id, "username": u.username, "role": u.role} for u in users]
        except Exception as e:
            print(f"[DB Error] get_all_users: {e}")
            return []
