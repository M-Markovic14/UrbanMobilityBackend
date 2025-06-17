import sqlite3
from datetime import datetime
import re
from modelEncryption.scooterEncryption import scooter_to_encrypted_row, row_to_scooter
from services.crypto_utils import decrypt, encrypt
from services.logCRUD import log_action
from role_permissions_config import ROLE_PERMISSIONS
from UrbanMobilityBackend.src.services import UserAuth


def prompt_valid(prompt_msg, validator, error_msg):
    while True:
        val = input(prompt_msg).strip()
        if val.lower() == "cancel":
            return None
        if validator(val):
            return val
        print(error_msg)

def create_scooter(conn, auth):
    if not auth.require_authentication():
        return
    if not auth.can("create_scooter"):
        print("Access denied: you do not have permission to create scooter data.")
        return

    cursor = conn.cursor()
    print("=== Register New Scooter === (Type 'cancel' to abort any field)")

    brand = prompt_valid("Brand: ", str.isalpha, "Only letters allowed.")
    if brand is None: return

    model = prompt_valid("Model: ", str.isalnum, "Only letters/numbers allowed.")
    if model is None: return

    serial = prompt_valid("Serial (10–17 chars): ", lambda x: re.fullmatch(r"[A-Za-z0-9]{10,17}", x), "Must be 10–17 alphanumeric characters.")
    if serial is None: return

    speed = prompt_valid("Top speed (km/h): ", lambda x: x.isdigit() and 0 < int(x) <= 200, "Enter number between 1 and 200.")
    if speed is None: return

    capacity = prompt_valid("Battery capacity (Wh): ", lambda x: x.replace('.', '', 1).isdigit() and float(x) > 0, "Must be a positive number.")
    if capacity is None: return

    soc = prompt_valid("State of Charge (%): ", lambda x: x.isdigit() and 0 <= int(x) <= 100, "Must be between 0 and 100.")
    if soc is None: return

    while True:
        target_soc = input("Target-range SoC (e.g. 20-80): ").strip()
        if target_soc.lower() == "cancel":
            return
        if re.fullmatch(r'\d{1,3}-\d{1,3}', target_soc):
            min_soc, max_soc = map(int, target_soc.split("-"))
            if 0 <= min_soc < max_soc <= 100:
                break
        print("Invalid range. Format: 20-80 (0 ≤ min < max ≤ 100).")

    while True:
        lat = input("Latitude (e.g. 51.92250): ").strip()
        lon = input("Longitude (e.g. 4.47917): ").strip()
        if lat.lower() == "cancel" or lon.lower() == "cancel":
            return
        if re.fullmatch(r'^-?\d{1,3}\.\d{5}$', lat) and re.fullmatch(r'^-?\d{1,3}\.\d{5}$', lon):
            lat_f, lon_f = float(lat), float(lon)
            if 51.85 <= lat_f <= 52.00 and 4.40 <= lon_f <= 4.60:
                break
        print("Invalid or out-of-bounds GPS coordinates.")

    out_of_service = prompt_valid("Out of service? (yes/no): ", lambda x: x.lower() in ("yes", "no"), "Enter 'yes' or 'no'")
    if out_of_service is None: return
    out_of_service = 1 if out_of_service.lower() == "yes" else 0

    mileage = prompt_valid("Mileage (km): ", lambda x: x.replace('.', '', 1).isdigit() and float(x) >= 0, "Must be 0 or more.")
    if mileage is None: return

    last_maintenance = prompt_valid("Last maintenance date (YYYY-MM-DD): ", lambda x: re.fullmatch(r'\d{4}-\d{2}-\d{2}', x), "Format must be YYYY-MM-DD.")
    if last_maintenance is None: return

    reg_date = datetime.now().isoformat()
    username = auth.get_current_user()["username"]

    try:
        cursor.execute('''
            INSERT INTO scooters (
                brand, model, serial_number, top_speed,
                battery_capacity, soc, target_soc_range,
                latitude, longitude, out_of_service,
                mileage, last_maintenance, in_service_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            encrypt(brand), encrypt(model), encrypt(serial), int(speed),
            float(capacity), int(soc), target_soc,
            encrypt(str(lat_f)), encrypt(str(lon_f)), out_of_service,
            float(mileage), last_maintenance, reg_date
        ))

        conn.commit()
        print("Scooter added successfully.")
        log_action(username, f"Added scooter {serial}", suspicious=False)

    except Exception as e:
        print(f"Error inserting scooter: {e}")
        log_action(username, f"Failed to add scooter {serial}: {e}", suspicious=True)



def search_scooters(conn, auth):
    if not auth.require_authentication():
        return
    if not auth.can("search_scooter"):
        print("Access denied: you do not have permission to search scooters.")
        return

    cursor = conn.cursor()
    term = input("Enter search term (brand, model, serial, or GPS): ").strip().lower()
    if not term:
        print("Search term cannot be empty.")
        return

    try:
        cursor.execute("SELECT * FROM scooters")
        results = cursor.fetchall()
    except Exception as e:
        print("Database error during scooter search.")
        log_action(auth.get_current_user()["username"], "Scooter search failed", suspicious=True)
        return

    matches = []
    for row in results:
        try:
            scooter = row_to_scooter(row)
            # Build combined searchable string
            searchable = " ".join([
                scooter.brand,
                scooter.model,
                scooter.serial_number,
                str(scooter.latitude),
                str(scooter.longitude)
            ]).lower()

            if term in searchable:
                matches.append((
                    scooter.serial_number,
                    scooter.brand,
                    scooter.model,
                    scooter.latitude,
                    scooter.longitude,
                    scooter.soc,
                    scooter.out_of_service
                ))
        except Exception:
            continue

    if not matches:
        print("No matching scooters found.")
        return

    print(f"\nFound {len(matches)} result(s):")
    for m in matches:
        print(
            f"Serial: {m[0]} | Brand: {m[1]} | Model: {m[2]} | "
            f"Lat: {m[3]} | Lon: {m[4]} | SoC: {m[5]}% | Out-of-service: {'Yes' if m[6] else 'No'}"
        )

    log_action(auth.get_current_user()["username"], f"Searched scooters with term '{term}'", suspicious=False)


def update_scooter(conn, auth):
    if not auth.require_authentication():
        return
    if not auth.can("update_scooter"):
        print("Access denied: you do not have permission to update scooters.")
        return

    role = auth.get_current_user()["role"]
    username = auth.get_current_user()["username"]
    cursor = conn.cursor()

    while True:
        serial = input("Enter serial number of scooter to update: ").strip()
        if not serial:
            print("Serial number is required.")
            continue

        encrypted_serial = encrypt(serial)
        cursor.execute("SELECT * FROM scooters WHERE serial_number = ?", (encrypted_serial,))
        row = cursor.fetchone()

        if not row:
            print("Scooter not found. Try again.")
        else:
            break

    scooter = row_to_scooter(row)

    # Role-based editable fields
    editable_fields = {
        "engineer": {
            "top_speed", "battery_capacity", "soc", "target_soc_range",
            "latitude", "longitude", "out_of_service", "mileage", "last_maintenance"
        },
        "sysadmin": set(),  # fallthrough to superadmin
        "superadmin": {
            "brand", "model", "serial_number", "top_speed", "battery_capacity", "soc",
            "target_soc_range", "latitude", "longitude", "out_of_service", "mileage", "last_maintenance"
        }
    }
    allowed_fields = editable_fields["superadmin"] if role != "engineer" else editable_fields["engineer"]

    def update_field(label, old_value, validator=str.isalnum, transform=lambda x: x):
        while True:
            val = input(f"{label} [{old_value}]: ").strip()
            if val == "":
                return old_value
            if validator(val):
                return transform(val)
            print("Invalid input. Try again.")

    updates = {}
    for field in scooter.__dict__:
        if field in ("id", "in_service_date"):
            continue
        if field not in allowed_fields:
            continue
        current_value = getattr(scooter, field)
        updated_value = update_field(field.replace('_', ' ').title(), current_value,
                                     lambda x: True, type(current_value))
        updates[field] = updated_value

    for k, v in updates.items():
        setattr(scooter, k, v)

    try:
        cursor.execute('''
            UPDATE scooters SET
                brand = ?, model = ?, serial_number = ?, top_speed = ?, battery_capacity = ?,
                soc = ?, target_soc_range = ?, latitude = ?, longitude = ?, out_of_service = ?,
                mileage = ?, last_maintenance = ?
            WHERE serial_number = ?
        ''', scooter_to_encrypted_row(scooter)[:-1] + (encrypted_serial,))
        conn.commit()
        print("Scooter updated successfully.")
        log_action(username, f"Updated scooter {serial}", suspicious=False)
    except Exception as e:
        print("Error during update:", e)
        log_action(username, f"Error updating scooter {serial}: {e}", suspicious=True)


def delete_scooter(conn, auth):
    if not auth.require_authentication():
        return
    if not auth.can("delete_scooter"):
        print("Access denied: you do not have permission to delete scooters.")
        return

    username = auth.get_current_user()["username"]
    cursor = conn.cursor()

    while True:
        serial = input("Enter serial number of scooter to delete: ").strip()
        if not serial:
            print("Serial number is required.")
            continue

        encrypted_serial = encrypt(serial)
        cursor.execute("SELECT brand, model FROM scooters WHERE serial_number = ?", (encrypted_serial,))
        result = cursor.fetchone()

        if not result:
            print("Scooter not found. Try again.")
        else:
            break

    brand, model = decrypt(result[0]), decrypt(result[1])
    confirm = input(f"Delete scooter {brand} {model} ({serial})? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Deletion cancelled.")
        return

    try:
        cursor.execute("DELETE FROM scooters WHERE serial_number = ?", (encrypted_serial,))
        conn.commit()
        print("Scooter deleted successfully.")
        log_action(username, f"Deleted scooter {serial}", suspicious=False)
    except Exception as e:
        print("Error deleting scooter:", e)
        log_action(username, f"Error deleting scooter {serial}: {e}", suspicious=True)
