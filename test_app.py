from auth import AuthManager
from database import DatabaseManager
import sys

def run_tests():
    print("--- Running CLINICOM Tests ---")
    
    # Test 1: Password Hashing (Does not require DB)
    try:
        auth = AuthManager()
        pwd = "testpassword123"
        hashed = auth.hash_password(pwd)
        if auth.verify_password(pwd, hashed):
            print("[OK] Password hashing and verification works.")
        else:
            print("[FAIL] Password verification failed.")
    except Exception as e:
        print(f"[FAIL] Password hashing exception: {e}")

    # Test 2: Database Connection
    try:
        db = DatabaseManager()
        if db.connect():
            print("[OK] Successfully connected to MySQL database.")
            db.disconnect()
        else:
            print("[FAIL] Could not connect to MySQL database.")
            print("       (This is expected if MySQL is not running, or if the 'clinicom' database hasn't been created yet).")
    except Exception as e:
        print(f"[FAIL] DB Connection exception: {e}")

if __name__ == "__main__":
    run_tests()
