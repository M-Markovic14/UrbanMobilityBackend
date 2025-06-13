import sqlite3
from datetime import datetime
import re
from services.crypto_utils import decrypt


def create_traveller(conn):
    cursor = conn.cursor()

    print("=== Register New Traveller ===")

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

        # Log the action
        log_action("admin_user", "Added new traveller", suspicious=False)

    except Exception as e:
        print(f"Error inserting traveller: {e}")


def search_travellers(conn, role, current_user):
    if role.lower() not in ("sysadmin", "superadmin"):
        print("Access denied: only SysAdmin and SuperAdmin can search traveller data.")
        return

    cursor = conn.cursor()
    print("Search by: 1) Name  2) Email  3) City  4) ID")
    option = input("Choose (1-4): ").strip()

    if option == "1":
        term = input("Enter name: ").strip()
        query = "SELECT * FROM travellers WHERE first_name || ' ' || last_name LIKE ?"
    elif option == "2":
        term = input("Enter email: ").strip()
        query = "SELECT * FROM travellers WHERE email LIKE ?"
    elif option == "3":
        term = input("Enter city: ").strip()
        query = "SELECT * FROM travellers WHERE city LIKE ?"
    elif option == "4":
        term = input("Enter ID: ").strip()
        if not term.isdigit():
            print("Invalid ID.")
            return
        query = "SELECT * FROM travellers WHERE id = ?"
        cursor.execute(query, (term,))
    else:
        print("Invalid choice.")
        return

    if option != "4":
        cursor.execute(query, (f"%{term}%",))

    results = cursor.fetchall()

    if not results:
        print("No matching traveller found.")
    else:
        print(f"\nFound {len(results)} result(s):")
        for row in results:
            print(f"ID: {row[0]} | Name: {row[1]} {row[2]} | City: {decrypt(row[8])} | Email: {decrypt(row[9])}")

    # Log the search
    log_action(current_user, f"Searched travellers with term '{term}'", suspicious=False)
