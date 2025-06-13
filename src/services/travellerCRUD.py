import sqlite3
from datetime import datetime
import re


def create_traveller(conn):
    cursor = conn.cursor()

    print("=== Register New Traveller ===")

    # Get user input with validation
    first_name = input("First Name: ").strip()
    last_name = input("Last Name: ").strip()

    birthday = input("Birthday (YYYY-MM-DD): ").strip()
    gender = input("Gender (male/female): ").strip().lower()
    street = input("Street: ").strip()
    house_number = input("House Number: ").strip()
    
    while True:
        zip_code = input("Zip Code (e.g. 1234AB): ").strip().upper()
        if re.match(r'^\d{4}[A-Z]{2}$', zip_code):
            break
        print("Invalid zip code format.")

    city = input("City: ").strip()
    email = input("Email: ").strip()

    while True:
        mobile = input("Mobile Phone (e.g. 612345678): ").strip()
        if re.match(r'^\d{8}$', mobile):
            break
        print("Invalid mobile number format.")

    while True:
        license_nr = input("Driving License Number (XDDDDDDDD or XXDDDDDDD): ").strip().upper()
        if re.match(r'^[A-Z]{1,2}\d{7,8}$', license_nr):
            break
        print("Invalid driving license format.")

    reg_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Insert into the database
    try:
        cursor.execute('''
            INSERT INTO travellers (
                first_name, last_name, birthday, gender,
                street, house_number, zip_code, city,
                email, mobile, driving_license, registration_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            first_name, last_name, birthday, gender,
            street, house_number, zip_code, city,
            email, mobile, license_nr, reg_date
        ))

        conn.commit()
        print("Traveller added successfully.")

        # Log the action (you will encrypt this in your log handler)
        log_action("admin_user", "Added new traveller", suspicious=False)

    except Exception as e:
        print(f"Error inserting traveller: {e}")
