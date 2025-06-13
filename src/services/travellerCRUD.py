import sqlite3
from datetime import datetime
import re


def create_traveller(conn):
    cursor = conn.cursor()

    print("=== Register New Traveller ===")

    # Get user input with validation
    while True:
        first_name = input("First Name: ").strip()
        if first_name.isalpha():
            break
        else:
            print("Invalid first name. Only letters allowed")

    while True:
        last_name = input("Last Name: ").strip()
        if last_name.isalpha():
            break
        else:
            print("Invalid last name. Only letters allowed")

    while True:
        birthday = input("Birthday (YYYY-MM-DD): ").strip()
        try:
            datetime.strptime(birthday, "%Y-%m-%d")
            break
        except ValueError:
            print("Invalid date. Please use format YYYY-MM-DD.")


    while True:
        gender = input("Gender (male/female): ").strip().lower()
        if gender in ("male", "female"):
            break
        else:
            print("Invalid input. Please enter 'male' or 'female'.")

    while True:
        street = input("Street: ").strip()
        if street.isalpha():
            break
        else:
            print("Invalid street name. Only letters allowed")

    while True:
        house_number = input("House Number: ").strip()
        if house_number.isdigit():
            break
        else: 
            print("Invalid House Number. Only numbers allowed")
    
    while True:
        zip_code = input("Zip Code (e.g. 1234AB): ").strip().upper()
        if re.match(r'^\d{4}[A-Z]{2}$', zip_code):
            break
        print("Invalid zip code format.")

    while True:
        city = input("city: ").strip()
        if city.isalpha():
            break
        else:
            print("Invalid city name. Only letters allowed")

    while True:
        email = input("Email address (e.g. example@mail.com): ").strip().lower()
        if re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email):
            break
        print("Invalid email format.")

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
                street_name, house_number, zip_code, city,
                email, mobile_phone, driving_license, registration_date
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

#def 