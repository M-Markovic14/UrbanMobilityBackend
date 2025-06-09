from dataclasses import dataclass
from datetime import datetime

@dataclass
class Traveller:
    id: int
    first_name: str
    last_name: str
    birthday: str
    gender: str
    street_name: str
    house_number: str
    zip_code: str
    city: str
    email: str
    mobile_phone: str
    driving_license: str
    registration_date: datetime
