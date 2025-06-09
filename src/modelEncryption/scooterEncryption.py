from typing import Tuple
from datetime import datetime
from models.scooter import Scooter
from services.crypto_utils import encrypt, decrypt


def scooter_to_encrypted_row(s: Scooter) -> Tuple:
    return (
        s.id,
        encrypt(s.brand),
        encrypt(s.model),
        encrypt(s.serial_number),
        s.top_speed,
        s.battery_capacity,
        s.soc,
        s.target_soc_range,
        encrypt(str(s.latitude)),   # Encrypt float as string
        encrypt(str(s.longitude)),  # Encrypt float as string
        s.out_of_service,
        s.mileage,
        s.last_maintenance,
        s.in_service_date.isoformat()
    )


def row_to_scooter(row: tuple) -> Scooter:
    return Scooter(
        id=row[0],
        brand=decrypt(row[1]),
        model=decrypt(row[2]),
        serial_number=decrypt(row[3]),
        top_speed=row[4],
        battery_capacity=row[5],
        soc=row[6],
        target_soc_range=row[7],
        latitude=float(decrypt(row[8])),
        longitude=float(decrypt(row[9])),
        out_of_service=bool(row[10]),
        mileage=row[11],
        last_maintenance=row[12],
        in_service_date=datetime.fromisoformat(row[13])
    )
