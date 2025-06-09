from dataclasses import dataclass
from datetime import datetime

@dataclass
class LogEntry:
    timestamp: datetime
    username: str
    activity: str
    additional_info: str
    suspicious: bool
