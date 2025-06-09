from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    username: str
    password_hash: str
    role: str  # 'super_admin', 'system_admin', or 'service_engineer'
    first_name: str
    last_name: str
    registration_date: datetime
