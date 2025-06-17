import sqlite3
import bcrypt
import re
import time
from datetime import datetime
from typing import Tuple
from models.user import User
from services.crypto_utils import encrypt, decrypt
from modelEncryption.userEncryption import row_to_user, verify_password, hash_password, user_to_encrypted_row
from utils.logger import log_action

# In-memory session
current_user = {
    "username": None,
    "role": None
}

SUPER_ADMIN_USERNAME = "super_admin"
SUPER_ADMIN_PASSWORD = "Admin_123?"

def validate_username(username):
    return re.match(r"^[a-zA-Z_][\w.'-]{7,9}$", username) is not None

def validate_password(password):
    return (
        12 <= len(password) <= 30 and
        re.search(r"[a-z]", password) and
        re.search(r"[A-Z]", password) and
        re.search(r"[0-9]", password) and
        re.search(r"[~!@#$%&_\-+=`|\\(){}\[\]:;'<>,.?/]", password)
    )

def insert_hardcoded_super_admin(conn):
    cursor = conn.cursor()
    hashed_pw = hash_password(SUPER_ADMIN_PASSWORD)
    try:
        cursor.execute("""
            INSERT INTO users (username, password_hash, role, first_name, last_name, registration_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            encrypt(SUPER_ADMIN_USERNAME),
            hashed_pw,
            "superadmin",
            encrypt("Super"),
            encrypt("Admin"),
            datetime.now().isoformat()
        ))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Already exists

def register_user(conn, creator_role):
    cursor = conn.cursor()
    print("=== Register New User ===")

    while True:
        username = input("Username (8-10 characters): ").strip().lower()
        if not validate_username(username):
            print("Invalid username format.")
            continue
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (encrypt(username),))
        if cursor.fetchone():
            print("Username already exists.")
        else:
            break

    while True:
        password = input("Password: ").strip()
        if not validate_password(password):
            print("Password does not meet complexity requirements.")
        else:
            break

    allowed_roles = ["engineer"]
    if creator_role == "superadmin":
        allowed_roles.append("sysadmin")

    while True:
        role = input(f"Role ({'/'.join(allowed_roles)}): ").strip().lower()
        if role in allowed_roles:
            break
        else:
            print("Invalid role selection.")

    first_name = input("First name: ").strip()
    last_name = input("Last name: ").strip()

    if not first_name.isalpha() or not last_name.isalpha():
        print("First and last names must contain only letters.")
        return

    user = User(
        username=username,
        password_hash=hash_password(password),
        role=role,
        first_name=first_name,
        last_name=last_name,
        registration_date=datetime.now()
    )

    cursor.execute("""
        INSERT INTO users (username, password_hash, role, first_name, last_name, registration_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, user_to_encrypted_row(user))

    conn.commit()
    print("User registered successfully.")
    log_action(current_user["username"], f"Registered new user '{username}'", suspicious=False)

def login(conn):
    global current_user
    attempts = 0

    while attempts < 3:
        username = input("Username: ").strip().lower()
        password = input("Password: ").strip()

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (encrypt(username),))
        row = cursor.fetchone()

        if row:
            user = row_to_user(row)
            if verify_password(password, user.password_hash):
                current_user["username"] = user.username
                current_user["role"] = user.role
                print(f"Login successful. Welcome {user.first_name} {user.last_name} ({user.role})")
                log_action(username, "Login successful", suspicious=False)
                return True

        print("Invalid username or password.")
        log_action(username, "Failed login attempt", suspicious=True)
        attempts += 1
        time.sleep(2)  # Delay to slow down brute-force attacks

    print("Too many failed attempts. Try again later.")
    return False
