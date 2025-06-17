from typing import Tuple
from models.log_entry import LogEntry
from services.crypto_utils import encrypt, decrypt
from datetime import datetime


def logentry_to_encrypted_row(log: LogEntry) -> Tuple:
    return (
        log.timestamp.isoformat(),
        encrypt(log.username),
        encrypt(log.activity),
        encrypt(log.additional_info),
        log.suspicious
    )

def row_to_logentry(row: tuple) -> LogEntry:
    return LogEntry(
        timestamp=datetime.fromisoformat(row[0]),
        username=decrypt(row[1]),
        activity=decrypt(row[2]),
        additional_info=decrypt(row[3]),
        suspicious=bool(row[4])
    )
