from datetime import datetime
from models.log_entry import LogEntry
from modelEncryption.logEncryption import logentry_to_encrypted_row

def log_action(username: str, activity: str, suspicious: bool = False, additional_info: str = "", conn=None):
    
    if conn is None:
        raise ValueError("Database connection must be provided to log_action")

    log = LogEntry(
        timestamp=datetime.now(),
        username=username,
        activity=activity,
        additional_info=additional_info,
        suspicious=suspicious
    )

    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO logs (timestamp, username, activity, additional_info, suspicious)
            VALUES (?, ?, ?, ?, ?)
        """, logentry_to_encrypted_row(log))
        conn.commit()
    except Exception as e:
        print(f"⚠️ Failed to log action: {e}")
