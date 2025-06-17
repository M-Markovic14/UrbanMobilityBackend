import sqlite3
import bcrypt
import re
import time
from datetime import datetime, timedelta
from typing import Tuple, Optional
from models.user import User
from services.crypto_utils import encrypt, decrypt
from modelEncryption.userEncryption import row_to_user, verify_password, hash_password, user_to_encrypted_row
from services.logCRUD import log_action
from role_permissions_config import ROLE_PERMISSIONS


class UserAuthentication:
    def __init__(self, db_connection):
        self.conn = db_connection
        self.current_user = {
            "username": None,
            "role": None,
            "first_name": None,
            "last_name": None,
            "login_time": None
        }
        self.failed_attempts = {}  # Track failed login attempts per IP/user
        self.max_attempts = 3
        self.lockout_duration = 300  # 5 minutes
        self.session_timeout = 1800  # 30 minutes
        
        # Constants
        self.SUPER_ADMIN_USERNAME = "super_admin"
        self.SUPER_ADMIN_PASSWORD = "Admin_123?"
        
        # Initialize super admin if not exists
        self.insert_hardcoded_super_admin()

    def can(self, action: str) -> bool:
        """Check if current user's role has permission for a specific action"""
        if not self.is_authenticated():
            return False
        role = self.current_user.get("role", "").lower()
        return ROLE_PERMISSIONS.get(role, {}).get(action, False)
    
    def validate_username(self, username: str) -> bool:
        """Validate username according to assignment requirements"""
        if not username:
            return False
        
        # Length check (8-10 characters)
        if len(username) < 8 or len(username) > 10:
            return False
            
        # Must start with letter or underscore
        if not re.match(r'^[a-zA-Z_]', username):
            return False
            
        # Can contain letters, numbers, underscores, apostrophes, periods
        if not re.match(r"^[a-zA-Z_][\w.'-]{7,9}$", username):
            return False
            
        return True

    def validate_password(self, password: str) -> Tuple[bool, str]:
        """Validate password with detailed error messages"""
        if not password:
            return False, "Password cannot be empty"
            
        if len(password) < 12 or len(password) > 30:
            return False, "Password must be between 12-30 characters"
            
        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter"
            
        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter"
            
        if not re.search(r"[0-9]", password):
            return False, "Password must contain at least one digit"
            
        if not re.search(r"[~!@#$%&_\-+=`|\\(){}\[\]:;'<>,.?/]", password):
            return False, "Password must contain at least one special character"
            
        return True, "Password is valid"

    def insert_hardcoded_super_admin(self):
        """Insert hardcoded super admin if not exists"""
        cursor = self.conn.cursor()
        hashed_pw = hash_password(self.SUPER_ADMIN_PASSWORD)
        try:
            cursor.execute("""
                INSERT INTO users (username, password_hash, role, first_name, last_name, registration_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                encrypt(self.SUPER_ADMIN_USERNAME),
                hashed_pw,
                "superadmin",
                encrypt("Super"),
                encrypt("Admin"),
                datetime.now().isoformat()
            ))
            self.conn.commit()
            log_action("SYSTEM", "Super admin account created", suspicious=False)
        except sqlite3.IntegrityError:
            pass  # Already exists

    def is_account_locked(self, username: str) -> Tuple[bool, int]:
        """Check if account is locked and return remaining lockout time"""
        if username in self.failed_attempts:
            attempts, last_attempt_time = self.failed_attempts[username]
            if attempts >= self.max_attempts:
                time_since_last = time.time() - last_attempt_time
                if time_since_last < self.lockout_duration:
                    remaining_time = int(self.lockout_duration - time_since_last)
                    return True, remaining_time
                else:
                    # Reset attempts after lockout period
                    del self.failed_attempts[username]
        return False, 0

    def record_failed_attempt(self, username: str):
        """Record a failed login attempt"""
        current_time = time.time()
        if username in self.failed_attempts:
            attempts, _ = self.failed_attempts[username]
            self.failed_attempts[username] = (attempts + 1, current_time)
        else:
            self.failed_attempts[username] = (1, current_time)

    def reset_failed_attempts(self, username: str):
        """Reset failed attempts for successful login"""
        if username in self.failed_attempts:
            del self.failed_attempts[username]

    def check_session_timeout(self) -> bool:
        """Check if current session has timed out"""
        if self.current_user["login_time"]:
            elapsed = time.time() - self.current_user["login_time"]
            if elapsed > self.session_timeout:
                self.logout()
                return True
        return False

    def login(self) -> bool:
        """Enhanced login with account lockout and session management"""
        attempts = 0
        max_login_attempts = 3

        print("=== LOGIN ===")
        
        while attempts < max_login_attempts:
            try:
                username = input("Username: ").strip().lower()
                
                # Check if account is locked
                is_locked, remaining_time = self.is_account_locked(username)
                if is_locked:
                    minutes = remaining_time // 60
                    seconds = remaining_time % 60
                    print(f"Account locked. Try again in {minutes}m {seconds}s")
                    log_action(username, "Login attempt on locked account", suspicious=True)
                    return False

                password = input("Password: ").strip()

                # Input validation
                if not username or not password:
                    print("Username and password are required.")
                    attempts += 1
                    continue

                cursor = self.conn.cursor()
                cursor.execute("SELECT * FROM users WHERE username = ?", (encrypt(username),))
                row = cursor.fetchone()

                if row:
                    user = row_to_user(row)
                    if verify_password(password, user.password_hash):
                        # Successful login
                        self.reset_failed_attempts(username)
                        
                        self.current_user = {
                            "username": user.username,
                            "role": user.role,
                            "first_name": user.first_name,
                            "last_name": user.last_name,
                            "login_time": time.time()
                        }
                        
                        print(f"Login successful. Welcome {user.first_name} {user.last_name} ({user.role})")
                        log_action(username, "Login successful", suspicious=False)
                        
                        return True

                # Failed login
                self.record_failed_attempt(username)
                print("Invalid username or password.")
                log_action(username, "Failed login attempt", suspicious=True)
                attempts += 1
                
                if attempts < max_login_attempts:
                    time.sleep(2)  # Delay to prevent brute force

            except KeyboardInterrupt:
                print("\nLogin cancelled.")
                return False
            except Exception as e:
                print(f"Login error: {str(e)}")
                log_action("UNKNOWN", f"Login error: {str(e)}", suspicious=True)
                attempts += 1

        print("Too many failed attempts. Please try again later.")
        return False

    def logout(self):
        """Logout current user"""
        if self.current_user["username"]:
            log_action(self.current_user["username"], "Logged out", suspicious=False)
            
        self.current_user = {
            "username": None,
            "role": None,
            "first_name": None,
            "last_name": None,
            "login_time": None
        }
        print("Logged out successfully.")

    def create_user(self):
        if not self.require_authentication():
            return
        if not (self.can("create_engineer") or self.can("create_sysadmin")):
            print("Access denied: you do not have permission to create users.")
            return

        username = self.current_user["username"]
        cursor = self.conn.cursor()

        print("=== Register New User ===")

        try:
            # Username validation
            while True:
                new_username = input("Username (8-10 characters): ").strip().lower()
                if not self.validate_username(new_username):
                    print("Invalid username format. Must be 8-10 characters, start with letter/underscore, and use only valid characters.")
                    continue
                cursor.execute("SELECT 1 FROM users WHERE username = ?", (encrypt(new_username),))
                if cursor.fetchone():
                    print("Username already exists.")
                else:
                    break

            # Password validation
            while True:
                password = input("Password: ").strip()
                is_valid, message = self.validate_password(password)
                if not is_valid:
                    print(f"Invalid password: {message}")
                else:
                    break

            # Determine allowed roles
            allowed_roles = []
            if self.can("create_engineer"):
                allowed_roles.append("engineer")
            if self.can("create_sysadmin"):
                allowed_roles.append("sysadmin")

            while True:
                print(f"Available roles: {', '.join(allowed_roles)}")
                selected_role = input("Role: ").strip().lower()
                if selected_role in allowed_roles:
                    break
                print("Invalid role selection.")

            # Name validation
            while True:
                first_name = input("First name: ").strip()
                last_name = input("Last name: ").strip()
                if not first_name or not last_name:
                    print("First and last names are required.")
                    continue
                if not first_name.replace(' ', '').replace('-', '').isalpha() or \
                not last_name.replace(' ', '').replace('-', '').isalpha():
                    print("Names must contain only letters, spaces, and hyphens.")
                    continue
                break

            # Create user object
            user = User(
                username=new_username,
                password_hash=hash_password(password),
                role=selected_role,
                first_name=first_name,
                last_name=last_name,
                registration_date=datetime.now()
            )

            cursor.execute("""
                INSERT INTO users (username, password_hash, role, first_name, last_name, registration_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, user_to_encrypted_row(user))

            self.conn.commit()
            print("User registered successfully.")
            log_action(username, f"Created user '{new_username}' with role '{selected_role}'", suspicious=False, conn=self.conn)
            return True

        except KeyboardInterrupt:
            print("\nUser creation cancelled.")
            return False
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            log_action(username, f"Error creating user: {str(e)}", suspicious=True, conn=self.conn)
            return False
        
        
    def update_password(self, target_username: str = None) -> bool:
        """Update password for current user or target user"""
        try:
            if target_username:
                # Admin updating another user's password
                if self.current_user["role"] not in ["superadmin", "sysadmin"]:
                    print("Insufficient permissions.")
                    return False
                username = target_username
            else:
                # User updating their own password
                username = self.current_user["username"]

            print(f"=== Updating Password for {username} ===")
            
            # Current password verification (except for admin reset)
            if not target_username or username == self.current_user["username"]:
                current_password = input("Current password: ").strip()
                cursor = self.conn.cursor()
                cursor.execute("SELECT password_hash FROM users WHERE username = ?", (encrypt(username),))
                row = cursor.fetchone()
                
                if not row or not verify_password(current_password, row[0]):
                    print("Current password is incorrect.")
                    log_action(self.current_user["username"], f"Failed password update attempt for {username}", suspicious=True)
                    return False

            # New password validation
            while True:
                new_password = input("New password: ").strip()
                is_valid, message = self.validate_password(new_password)
                if not is_valid:
                    print(f"Invalid password: {message}")
                else:
                    break

            confirm_password = input("Confirm new password: ").strip()
            if new_password != confirm_password:
                print("Passwords do not match.")
                return False

            # Update password
            cursor = self.conn.cursor()
            new_hash = hash_password(new_password)
            cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", 
                         (new_hash, encrypt(username)))
            self.conn.commit()

            print("Password updated successfully.")
            log_action(self.current_user["username"], f"Password updated for user '{username}'", suspicious=False)
            return True

        except KeyboardInterrupt:
            print("\nPassword update cancelled.")
            return False
        except Exception as e:
            print(f"Password update error: {str(e)}")
            log_action(self.current_user["username"], f"Password update error: {str(e)}", suspicious=True)
            return False

    def is_authenticated(self) -> bool:
        """Check if user is authenticated and session is valid"""
        if not self.current_user["username"]:
            return False
            
        if self.check_session_timeout():
            print("Session expired. Please login again.")
            return False
            
        return True

    def get_current_user(self) -> dict:
        """Get current user information"""
        return self.current_user.copy()

    def require_authentication(self) -> bool:
        """Return True if user is authenticated, else print and return False"""
        if not self.is_authenticated():
            print("Please login first.")
            return False
        return True

