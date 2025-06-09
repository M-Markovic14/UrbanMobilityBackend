from dataclasses import dataclass
from datetime import datetime

@dataclass
class Scooter:
    id: int
    brand: str
    model: str
    serial_number: str
    top_speed: float
    battery_capacity: float
    soc: int  # State of Charge (%)
    target_soc_range: str  # e.g. "20-80"
    latitude: float
    longitude: float
    out_of_service: bool
    mileage: float
    last_maintenance: str  # "YYYY-MM-DD"
    in_service_date: datetime
