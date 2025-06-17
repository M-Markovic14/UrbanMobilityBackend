import sqlite3
from datetime import datetime
import re
from services.crypto_utils import decrypt, encrypt

Citylist = [
    "amsterdam", "rotterdam", "schiedam", "utrecht", "eindhoven",
    "tilburg", "groningen", "almere", "breda", "nijmegen"
]


def create_traveller(conn, role, current_user):
    if role.lower() not in ("sysadmin", "superadmin"):
        print("Access denied: only SysAdmin and SuperAdmin can search traveller data.")
        return
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


def search_travellers(conn, role, current_user):
    if role.lower() not in ("sysadmin", "superadmin"):
        print("Access denied: only SysAdmin and SuperAdmin can search traveller data.")
        return

    cursor = conn.cursor()
    
    while True:
        print("Search by: 1) Name  2) Email  3) City  4) ID")
        option = input("Choose (1-4): ").strip()
        if option in ("1", "2", "3", "4"):
            break
        else:
            print("Invalid option. Choose a number between 1 and 4.")

    if option == "1":
        term = input("Enter name: ").strip()
        if not term.replace(" ", "").isalpha():
            print("Invalid name. Only letters and spaces are allowed.")
            return
        query = "SELECT * FROM travellers WHERE first_name || ' ' || last_name LIKE ?"
        param = (f"%{term}%",)

    elif option == "2":
        term = input("Enter email: ").strip().lower()
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", term):
            print("Invalid email format.")
            return
        query = "SELECT * FROM travellers WHERE email LIKE ?"
        param = (f"%{term}%",)

    elif option == "3":
        term = input("Enter city: ").strip()
        if not term.isalpha():
            print("Invalid city name. Only letters allowed.")
            return
        query = "SELECT * FROM travellers WHERE city LIKE ?"
        param = (f"%{term}%",)

    elif option == "4":
        term = input("Enter ID: ").strip()
        if not term.isdigit():
            print("Invalid ID. Only digits are allowed.")
            return
        query = "SELECT * FROM travellers WHERE id = ?"
        param = (term,)

    cursor.execute(query, param)
    results = cursor.fetchall()

    if not results:
        print("No matching traveller found.")
        return

    print(f"\nFound {len(results)} result(s):")
    for row in results:
        try:
            city = decrypt(row[8])
            email = decrypt(row[9])
        except Exception as e:
            print("Error decrypting data.")
            log_action(current_user, "Decryption failed during search", suspicious=True)
            return

        print(f"ID: {row[0]} | Name: {row[1]} {row[2]} | City: {city} | Email: {email}")

    # Log the search
    log_action(current_user, f"Searched travellers with term '{term}'", suspicious=False)



def Update_traveller(conn, role, current_user):
    if role.lower() not in ("sysadmin", "superadmin"):
        print("Access denied: only SysAdmin and SuperAdmin can update traveller data.")
        return

    cursor = conn.cursor()

    def prompt_update(label, old_value, is_encrypted=False, validator=None):
        value = decrypt(old_value) if is_encrypted else old_value

        while True:
            new = input(f"{label} [{value}]: ").strip()

            if new == "":
                return old_value  # keep current value

            if validator and not validator(new):
                print(f"Invalid {label}. Please try again.")
                continue  # ask again

            return encrypt(new) if is_encrypted else new

    while True:
        print("Search by: 1) Name  2) ID")
        option = input("Choose (1-2): ").strip()
        if option in ("1", "2"):
            break
        else:
            print("Invalid option. Choose the number 1 or 2.")

    if option == "1":
        first = input("Enter first name: ").strip()
        last = input("Enter last name: ").strip()
        if not first.isalpha() or not last.isalpha():
            print("Invalid input. First and last names must contain only letters.")
            return

        encrypted_first = encrypt(first)
        encrypted_last = encrypt(last)

        query = """
            SELECT first_name, last_name, birthday, gender,
                street_name, house_number, zip_code, city,
                email, mobile_phone, driving_license
            FROM travellers
            WHERE first_name = ? AND last_name = ?
        """
        param = (encrypted_first, encrypted_last)

    elif option == "2":
        traveller_id = input("Enter traveller ID: ").strip()
        if not traveller_id.isdigit():
            print("Invalid ID.")
            return

        query = """
            SELECT first_name, last_name, birthday, gender,
                street_name, house_number, zip_code, city,
                email, mobile_phone, driving_license
            FROM travellers
            WHERE id = ?
        """
        param = (traveller_id,)

    cursor.execute(query, param)
    results = cursor.fetchall()

    if not results:
        if option == "2":
            print(f"No traveller found with ID {traveller_id}.")
        else:
            print(f"No traveller found with name {first} {last}.")
        return

    if len(results) > 1:
        print("\nMultiple travellers found:")
        for i, row in enumerate(results):
            print(f"{i+1}) {decrypt(row[0])} {decrypt(row[1])}")
        choice = input("Select traveller number to update: ").strip()
        if not choice.isdigit() or not (1 <= int(choice) <= len(results)):
            print("Invalid selection.")
            return
        selected = results[int(choice) - 1]
    else:
        selected = results[0]

    print("\nTraveller found:")
    try:
        print(
            f"Name: {decrypt(selected[0])} {decrypt(selected[1])} | Birthday: {selected[2]} | Gender: {selected[3]} | "
            f"Address: {decrypt(selected[4])} {selected[5]}, {selected[6]} {decrypt(selected[7])} | "
            f"Email: {decrypt(selected[8])} | Phone: {decrypt(selected[9])} | License: {selected[10]}"
        )
    except Exception as e:
        print("Error decrypting data.")
        log_action(current_user, "Decryption failed during update", suspicious=True)
        return

    updated = {}
    updated["first_name"] = prompt_update("First name", selected[0], is_encrypted=True, validator=str.isalpha)
    updated["last_name"] = prompt_update("Last name", selected[1], is_encrypted=True, validator=str.isalpha)
    updated["birthday"] = prompt_update("Birthday (YYYY-MM-DD)", selected[2], validator=lambda d: re.match(r"^\d{4}-\d{2}-\d{2}$", d))
    updated["gender"] = prompt_update("Gender (male/female)", selected[3], validator=lambda g: g.lower() in ("male", "female"))
    updated["street_name"] = prompt_update("Street", selected[4], is_encrypted=True)
    updated["house_number"] = prompt_update("House number", selected[5], validator=str.isdigit)
    updated["zip_code"] = prompt_update("Zip code", selected[6], validator=lambda z: re.match(r"^\d{4}[A-Z]{2}$", z))
    updated["city"] = prompt_update("City", selected[7], is_encrypted=True)
    updated["email"] = prompt_update("Email", selected[8], is_encrypted=True, validator=lambda e: re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", e))
    updated["mobile_phone"] = prompt_update("Phone (8 digits)", selected[9], is_encrypted=True, validator=lambda p: re.match(r"^\d{8}$", p))
    updated["driving_license"] = prompt_update("Driving license", selected[10], validator=lambda d: re.match(r"^[A-Z]{1,2}\d{7,8}$", d))

    if None in updated.values():
        print("Update canceled due to invalid input.")
        return

    # Use ID or full name to identify the record
    if option == "1":
        where_clause = "WHERE first_name = ? AND last_name = ?"
        where_param = (selected[0], selected[1])
    else:
        where_clause = "WHERE id = ?"
        where_param = (param[0],)

    cursor.execute(f"""
        UPDATE travellers SET
            first_name = ?, last_name = ?, birthday = ?, gender = ?,
            street_name = ?, house_number = ?, zip_code = ?, city = ?,
            email = ?, mobile_phone = ?, driving_license = ?
        {where_clause}
    """, (
        updated["first_name"], updated["last_name"], updated["birthday"], updated["gender"],
        updated["street_name"], updated["house_number"], updated["zip_code"], updated["city"],
        updated["email"], updated["mobile_phone"], updated["driving_license"],
        *where_param
    ))

    conn.commit()
    print("Traveller updated successfully.")
    log_action(current_user, "Updated traveller data", suspicious=False)


def Delete_traveller(conn, role, current_user):
    if role.lower() not in ("sysadmin", "superadmin"):
        print("Access denied: only SysAdmin and SuperAdmin can delete traveller data.")
        return

    cursor = conn.cursor()

    while True:
        print("Delete traveller by ID")
        traveller_id = input("Enter traveller ID: ").strip()
        if not traveller_id.isdigit():
            print("Invalid ID. Please enter digits only.")
            continue

        # Check if traveller exists
        query = """
            SELECT first_name, last_name, email
            FROM travellers
            WHERE id = ?
        """
        cursor.execute(query, (traveller_id,))
        result = cursor.fetchone()

        if not result:
            print(f"No traveller found with ID {traveller_id}.")
            return

        try:
            name = f"{decrypt(result[0])} {decrypt(result[1])}"
            email = decrypt(result[2])
        except:
            print("Error decrypting traveller info.")
            return

        print(f"\nTraveller found:\nName: {name}\nEmail: {email}")
        confirm = input("Are you sure you want to delete this traveller? (y/n): ").strip().lower()
        if confirm == "y":
            cursor.execute("DELETE FROM travellers WHERE id = ?", (traveller_id,))
            conn.commit()
            print("Traveller deleted successfully.")
            log_action(current_user, f"Deleted traveller ID {traveller_id}", suspicious=False)
        else:
            print("Deletion cancelled.")
        break
