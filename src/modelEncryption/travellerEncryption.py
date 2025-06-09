from typing import Tuple
from datetime import datetime
from models.traveller import Traveller
from services.crypto_utils import encrypt, decrypt

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

def row_to_traveller(row: tuple) -> Traveller:
    return Traveller(
        id=row[0],
        first_name=decrypt(row[1]),
        last_name=decrypt(row[2]),
        birthday=row[3],
        gender=row[4],
        street_name=decrypt(row[5]),
        house_number=decrypt(row[6]),
        zip_code=decrypt(row[7]),
        city=decrypt(row[8]),
        email=decrypt(row[9]),
        mobile_phone=decrypt(row[10]),
        driving_license=decrypt(row[11]),
        registration_date=datetime.fromisoformat(row[12])
    )
