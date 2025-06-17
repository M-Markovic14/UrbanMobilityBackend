import sqlite3
import re
from datetime import datetime
from services.crypto_utils import decrypt, encrypt
from utils.logger import log_action

Citylist = [
    "amsterdam", "rotterdam", "schiedam", "utrecht", "eindhoven",
    "tilburg", "groningen", "almere", "breda", "nijmegen"
]

def prompt_valid(prompt_msg, validator, error_msg, is_encrypted=False):
    while True:
        val = input(prompt_msg).strip()
        if val.lower() == "cancel":
            return None
        if validator(val):
            return encrypt(val) if is_encrypted else val
        print(error_msg)

def add_traveller(conn, auth):
    if not auth.require_authentication():
        return
    if not auth.can("add_traveller"):
        print("Access denied: you do not have permission to add travellers.")
        return

    username = auth.get_current_user()["username"]
    cursor = conn.cursor()

    print("=== Register New Traveller === (Type 'cancel' to abort any field)")

    first_name = prompt_valid("First Name: ", str.isalpha, "Only letters allowed", is_encrypted=True)
    if first_name is None: return

    last_name = prompt_valid("Last Name: ", str.isalpha, "Only letters allowed", is_encrypted=True)
    if last_name is None: return

    birthday = prompt_valid("Birthday (YYYY-MM-DD): ",
                            lambda x: re.fullmatch(r"\d{4}-\d{2}-\d{2}", x),
                            "Invalid date format (YYYY-MM-DD)")
    if birthday is None: return

    gender = prompt_valid("Gender (male/female): ",
                          lambda x: x.lower() in ("male", "female"),
                          "Must be 'male' or 'female'")
    if gender is None: return

    street = prompt_valid("Street Name: ",
                          lambda x: x.replace(" ", "").isalpha(),
                          "Only letters and spaces allowed",
                          is_encrypted=True)
    if street is None: return

    house_number = prompt_valid("House Number: ",
                                lambda x: x.isdigit(),
                                "Only digits allowed")
    if house_number is None: return

    zip_code = prompt_valid("Zip Code (e.g. 1234AB): ",
                            lambda x: re.fullmatch(r"\d{4}[A-Z]{2}", x),
                            "Invalid zip format (1234AB)")
    if zip_code is None: return

    city = prompt_valid("City: ",
                        lambda x: x.lower() in Citylist,
                        "City not allowed",
                        is_encrypted=True)
    if city is None: return

    email = prompt_valid("Email: ",
                         lambda x: re.fullmatch(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", x),
                         "Invalid email format",
                         is_encrypted=True)
    if email is None: return

    mobile = prompt_valid("Mobile Phone (e.g. 612345678): ",
                          lambda x: re.fullmatch(r"^6\d{8}$", x),
                          "Must be 9 digits, starting with 6",
                          is_encrypted=True)
    if mobile is None: return

    license_nr = prompt_valid("Driving License (XDDDDDDDD or XXDDDDDDD): ",
                              lambda x: re.fullmatch(r"^[A-Z]{1,2}\d{7,8}$", x),
                              "Invalid license format")
    if license_nr is None: return

    reg_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
        log_action(username, "Added new traveller", suspicious=False)

    except Exception as e:
        print(f"Error inserting traveller: {e}")
        log_action(username, f"Error adding traveller: {e}", suspicious=True)


def search_traveller(conn, auth):
    if not auth.require_authentication():
        return
    if not auth.can("search_traveller"):
        print("Access denied: you do not have permission to search traveller data.")
        return

    username = auth.get_current_user()["username"]
    cursor = conn.cursor()

    while True:
        print("Search by: 1) Name  2) Email  3) City  4) ID")
        option = input("Choose (1-4): ").strip()
        if option in ("1", "2", "3", "4"):
            break
        print("Invalid option. Choose a number between 1 and 4.")

    term = input("Enter search term: ").strip().lower()
    if not term:
        print("Search term cannot be empty.")
        return

    try:
        cursor.execute("SELECT * FROM travellers")
        results = cursor.fetchall()
    except Exception as e:
        print("Database error during search.")
        log_action(username, "Search query failed", suspicious=True)
        return

    matches = []
    for row in results:
        try:
            decrypted_fields = {
                "id": str(row[0]),
                "first_name": decrypt(row[1]).lower(),
                "last_name": decrypt(row[2]).lower(),
                "city": decrypt(row[8]).lower(),
                "email": decrypt(row[9]).lower(),
            }

            combined_name = f"{decrypted_fields['first_name']} {decrypted_fields['last_name']}"

            if (term in decrypted_fields['id'] or
                term in decrypted_fields['first_name'] or
                term in decrypted_fields['last_name'] or
                term in combined_name or
                term in decrypted_fields['email'] or
                term in decrypted_fields['city']):
                matches.append((
                    row[0],
                    decrypted_fields['first_name'],
                    decrypted_fields['last_name'],
                    decrypted_fields['city'],
                    decrypted_fields['email']
                ))

        except Exception:
            continue

    if not matches:
        print("No matching traveller found.")
        return

    print(f"\nFound {len(matches)} result(s):")
    for match in matches:
        print(f"ID: {match[0]} | Name: {match[1].title()} {match[2].title()} | City: {match[3].title()} | Email: {match[4]}")

    log_action(username, f"Searched travellers with partial key '{term}'", suspicious=False)



def update_traveller(conn, auth):
    if not auth.require_authentication():
        return
    if not auth.can("update_traveller"):
        print("Access denied: you do not have permission to update traveller data.")
        return

    username = auth.get_current_user()["username"]
    cursor = conn.cursor()

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
            print("Invalid input. Names must contain only letters.")
            return
        query = """
            SELECT id, first_name, last_name, birthday, gender,
                   street_name, house_number, zip_code, city,
                   email, mobile_phone, driving_license
            FROM travellers
            WHERE first_name = ? AND last_name = ?
        """
        param = (encrypt(first), encrypt(last))

    else:
        traveller_id = input("Enter traveller ID: ").strip()
        if not traveller_id.isdigit():
            print("Invalid ID.")
            return
        query = """
            SELECT id, first_name, last_name, birthday, gender,
                   street_name, house_number, zip_code, city,
                   email, mobile_phone, driving_license
            FROM travellers
            WHERE id = ?
        """
        param = (traveller_id,)

    cursor.execute(query, param)
    results = cursor.fetchall()

    if not results:
        print("No matching traveller found.")
        return

    selected = results[0]
    traveller_id = selected[0]

    print("\nTraveller found:")
    try:
        print(
            f"Name: {decrypt(selected[1])} {decrypt(selected[2])} | Birthday: {selected[3]} | Gender: {selected[4]} | "
            f"Address: {decrypt(selected[5])} {selected[6]}, {selected[7]} {decrypt(selected[8])} | "
            f"Email: {decrypt(selected[9])} | Phone: {decrypt(selected[10])} | License: {selected[11]}"
        )
    except Exception:
        print("Error decrypting data.")
        log_action(username, "Decryption failed during traveller update", suspicious=True)
        return

    def prompt_update(label, old_value, is_encrypted=False, validator=None):
        current = decrypt(old_value) if is_encrypted else old_value
        while True:
            new = input(f"{label} [{current}]: ").strip()
            if new == "":
                return old_value
            if validator and not validator(new):
                print(f"Invalid {label}. Try again.")
                continue
            return encrypt(new) if is_encrypted else new

    updated = {
        "first_name": prompt_update("First name", selected[1], True, str.isalpha),
        "last_name": prompt_update("Last name", selected[2], True, str.isalpha),
        "birthday": prompt_update("Birthday (YYYY-MM-DD)", selected[3], False, lambda d: re.fullmatch(r"\d{4}-\d{2}-\d{2}", d)),
        "gender": prompt_update("Gender", selected[4], False, lambda g: g.lower() in ("male", "female")),
        "street_name": prompt_update("Street", selected[5], True),
        "house_number": prompt_update("House number", selected[6], False, str.isdigit),
        "zip_code": prompt_update("Zip Code", selected[7], False, lambda z: re.fullmatch(r"\d{4}[A-Z]{2}", z)),
        "city": prompt_update("City", selected[8], True),
        "email": prompt_update("Email", selected[9], True, lambda e: re.fullmatch(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", e)),
        "mobile_phone": prompt_update("Phone", selected[10], True, lambda p: re.fullmatch(r"^6\d{8}$", p)),
        "driving_license": prompt_update("License", selected[11], False, lambda d: re.fullmatch(r"^[A-Z]{1,2}\d{7,8}$", d))
    }

    try:
        cursor.execute("""
            UPDATE travellers SET
                first_name = ?, last_name = ?, birthday = ?, gender = ?,
                street_name = ?, house_number = ?, zip_code = ?, city = ?,
                email = ?, mobile_phone = ?, driving_license = ?
            WHERE id = ?
        """, (
            updated["first_name"], updated["last_name"], updated["birthday"], updated["gender"],
            updated["street_name"], updated["house_number"], updated["zip_code"], updated["city"],
            updated["email"], updated["mobile_phone"], updated["driving_license"],
            traveller_id
        ))

        conn.commit()
        print("Traveller updated successfully.")
        log_action(username, f"Updated traveller ID {traveller_id}", suspicious=False)
    except Exception as e:
        print("Error during update:", e)
        log_action(username, f"Error updating traveller ID {traveller_id}: {e}", suspicious=True)



def delete_traveller(conn, auth):
    if not auth.require_authentication():
        return
    if not auth.can("delete_traveller"):
        print("Access denied: you do not have permission to delete travellers.")
        return

    username = auth.get_current_user()["username"]
    cursor = conn.cursor()

    while True:
        traveller_id = input("Enter traveller ID to delete: ").strip()
        if not traveller_id.isdigit():
            print("Invalid ID. Please enter digits only.")
            continue

        try:
            cursor.execute("SELECT first_name, last_name, email FROM travellers WHERE id = ?", (traveller_id,))
            result = cursor.fetchone()
        except Exception as e:
            print("Database error while fetching traveller.")
            log_action(username, f"DB error fetching traveller ID {traveller_id}: {e}", suspicious=True)
            return

        if not result:
            print(f"No traveller found with ID {traveller_id}.")
            return

        try:
            name = f"{decrypt(result[0])} {decrypt(result[1])}"
            email = decrypt(result[2])
        except Exception as e:
            print("Error decrypting traveller info.")
            log_action(username, f"Decryption failed for traveller ID {traveller_id}: {e}", suspicious=True)
            return

        print(f"\nTraveller found:\nName: {name}\nEmail: {email}")
        confirm = input("Are you sure you want to delete this traveller? (y/n): ").strip().lower()
        if confirm == "y":
            try:
                cursor.execute("DELETE FROM travellers WHERE id = ?", (traveller_id,))
                conn.commit()
                print("Traveller deleted successfully.")
                log_action(username, f"Deleted traveller ID {traveller_id}", suspicious=False)
            except Exception as e:
                print("Error deleting traveller.")
                log_action(username, f"Error deleting traveller ID {traveller_id}: {e}", suspicious=True)
            break
        else:
            print("Deletion cancelled.")
            break


