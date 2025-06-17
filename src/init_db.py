import sqlite3
import os

# Ensure db is created in the same folder as this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "urban_mobility.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    registration_date TEXT
)
''')

# Create travellers table
cursor.execute('''
CREATE TABLE IF NOT EXISTS travellers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    birthday TEXT NOT NULL,
    gender TEXT NOT NULL,
    street_name TEXT NOT NULL,
    house_number TEXT NOT NULL,
    zip_code TEXT NOT NULL,
    city TEXT NOT NULL,
    email TEXT NOT NULL,
    mobile_phone TEXT NOT NULL,
    driving_license TEXT NOT NULL,
    registration_date TEXT NOT NULL
)
''')

# Create scooters table
cursor.execute('''
CREATE TABLE IF NOT EXISTS scooters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand TEXT NOT NULL,
    model TEXT NOT NULL,
    serial_number TEXT NOT NULL UNIQUE,
    top_speed REAL NOT NULL,
    battery_capacity REAL NOT NULL,
    soc INTEGER NOT NULL,
    target_soc_range TEXT NOT NULL,
    latitude REAL,
    longitude REAL,
    out_of_service INTEGER DEFAULT 0,
    mileage REAL,
    last_maintenance TEXT,
    in_service_date TEXT
)
''')

# Create log_entries table
cursor.execute('''
CREATE TABLE IF NOT EXISTS log_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    username TEXT NOT NULL,
    activity TEXT NOT NULL,
    additional_info TEXT,
    suspicious INTEGER DEFAULT 0
)
''')

conn.commit()
conn.close()

print(f"Database initialized at {db_path}")
