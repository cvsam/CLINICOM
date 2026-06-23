import sys
from sqlalchemy import text

from auth import AuthManager
from database import engine, USE_MOCK, init_db
from controllers import PatientManager


def run_tests():
    print("--- Running CLINICOM Tests ---")
    
    # Test 1: Password Hashing (Does not require DB)
    try:
        auth = AuthManager()
        pwd = "testpassword123"
        hashed = auth._hash_password(pwd)
        if auth._verify_password(pwd, hashed):
            print("[OK] Password hashing and verification works.")
        else:
            print("[FAIL] Password verification failed.")
    except Exception as e:
        print(f"[FAIL] Password hashing exception: {e}")

    # Test 2: Database Connection
    try:
        init_db()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
            db_type = "SQLite (Mock)" if USE_MOCK else "MySQL (Production)"
            print(f"[OK] Successfully connected to {db_type} database via SQLAlchemy.")
    except Exception as e:
        print(f"[FAIL] DB Connection exception: {e}")
        print("       (Make sure MySQL is running if USE_MOCK=False).")

    # Test 3: Input Validation (BaseManager via PatientManager)
    try:
        pm = PatientManager()
        if pm._validate_name("John Doe") and not pm._validate_name("John123"):
            print("[OK] Name validation works.")
        else:
            print("[FAIL] Name validation failed.")
            
        if pm._validate_date("2024-01-15") and not pm._validate_date("15-01-2024"):
            print("[OK] Date validation works.")
        else:
            print("[FAIL] Date validation failed.")
            
        if pm._validate_phone("0712345678") and not pm._validate_phone("invalid"):
            print("[OK] Phone validation works.")
        else:
            print("[FAIL] Phone validation failed.")
    except Exception as e:
        print(f"[FAIL] Validation tests exception: {e}")

if __name__ == "__main__":
    run_tests()
