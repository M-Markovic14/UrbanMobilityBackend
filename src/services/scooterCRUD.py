import sqlite3
from datetime import datetime
import re
from services.crypto_utils import decrypt, encrypt


def create_scooter(conn, role, current_user):
    if role.lower() not in ("sysadmin", "superadmin"):
        print("Access denied: only SysAdmin and SuperAdmin can create an traveller data.")
        return
    cursor = conn.cursor()

    print("=== Register New Scooter ===")

    while True:
        brand = input("Brand Name: ").strip()
        if brand.isalpha():
            break
        else:
            print("Invalid brand name. Only letters allowed")

    while True:
        model = input("Model: ").strip()
        if model.isalpha():
            break
        else:
            print("Invalid model. Only letters allowed")

    while True:
        serialnumber = input("Serial number (10–17 letters): ").strip()
        
        if serialnumber.isalpha():
            length = len(serialnumber)
            if length >= 10 and length <= 17:
                break
            elif length < 10:
                print("Serial number is too short. Minimum 10 characters.")
            else:
                print("Serial number is too long. Maximum 17 characters.")
        else:
            print("Serial number must only contain letters (A–Z).")

    while True:
        speed = input("Enter speed (e.g. 120kmh): ").strip().lower()
        if re.match(r'^\d{1,3}\s?kmh$', speed):
            print("Valid speed!")
            break
        else:
            print("Invalid format. Please enter like '120kmh' or '120 kmh'.")

    while True:
        soc_range = input("Enter Target-range SoC (e.g. 20-80): ").strip()
        if re.match(r'^\d{1,3}-\d{1,3}$', soc_range):
            min_soc, max_soc = map(int, soc_range.split("-"))
            if 0 <= min_soc < max_soc <= 100:
                print(f"Valid range: {min_soc}-{max_soc}%")
                break
            else:
                print("Values must be between 0 and 100, and min < max.")
        else:
            print("Invalid format. Use two numbers like 20-80.")
        while True:
            house_number = input("House Number: ").strip()
            if house_number.isdigit():
                break
            else: 
                print("Invalid House Number. Only numbers allowed")
    
    while True:
        lat = input("Enter latitude (e.g. 51.92250): ").strip()
        lon = input("Enter longitude (e.g. 4.47917): ").strip()

        if re.match(r'^-?\d{1,3}\.\d{5}$', lat) and re.match(r'^-?\d{1,3}\.\d{5}$', lon):
            lat_f = float(lat)
            lon_f = float(lon)

            if 51.85 <= lat_f <= 52.00 and 4.40 <= lon_f <= 4.60:
                print("Valid Rotterdam GPS location.")
                break
            else:
                print("Coordinates must be within the Rotterdam region (lat 51.85–52.00, lon 4.40–4.60).")
        else:
            print("Invalid GPS format. Use exactly 5 decimals like 51.92250.")

    while True:
        city = input("City: ").lower().strip()
        
        if city.isalpha():
            if city in Citylist:
                print(f"City '{city.title()}' is valid.")
                break
            else:
                print("Invalid city. Choose a city that is allowed.")
        else:
            print("Invalid city name. Only letters allowed.")

    while True:
        email = input("Email address (e.g. example@mail.com): ").strip().lower()
        if re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email):
            break
        print("Invalid email format.")

    while True:
        mobile = input("Mobile Phone (e.g. 612345678): ").strip()
        if re.match(r'^6\d{8}$', mobile):
            break
        print("Invalid mobile number format. It should start with 6 and have 9 digits total (e.g. 612345678).")

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


