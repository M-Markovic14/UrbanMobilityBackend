import sqlite3
from datetime import datetime
from models import Traveller
from crypto_utils import encrypt
from typing import Tuple

def traveller_to_encrypted_row(t: Traveller) -> Tuple:
    return (
        t.id,
        encrypt(t.first_name),
        encrypt(t.last_name),
        t.birthday,
        t.gender,
        encrypt(t.street_name),
        encrypt(t.house_number),
        encrypt(t.zip_code),
        encrypt(t.city),
        encrypt(t.email),
        encrypt(t.mobile_phone),
        encrypt(t.driving_license),
        t.registration_date.isoformat()
    )

def add_new_traveller(conn, traveller: Traveller):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO travellers (
            id, first_name, last_name, birthday, gender,
            street_name, house_number, zip_code, city,
            email, mobile_phone, driving_license, registration_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, traveller_to_encrypted_row(traveller))
    conn.commit()
