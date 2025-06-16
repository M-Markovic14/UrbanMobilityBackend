import sqlite3
from services.UserAuth import (
    login,
    register_user,
    insert_hardcoded_super_admin,
    current_user
)

def main():
    conn = sqlite3.connect("urban_mobility.db")
    insert_hardcoded_super_admin(conn)

    while True:
        print("\n=== Main Menu ===")
        print("1. Login")
        print("2. Register New User")
        print("3. Exit")
        action = input("Choose an option: ").strip()

        if action == "1":
            if login(conn):
                print(f"You are logged in as: {current_user['username']} with role: {current_user['role']}")
            else:
                print("Access denied.")

        elif action == "2":
            if current_user["role"] in ("superadmin", "sysadmin"):
                register_user(conn, current_user["role"])
            else:
                print("You must be logged in as a sysadmin or superadmin to register users.")

        elif action == "3":
            print("in the making ...")
            break

        else:
            print("Invalid option. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()
