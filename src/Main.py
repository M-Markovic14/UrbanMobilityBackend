import sqlite3
from services.UserAuth import UserAuthentication
from services.scooterCRUD import create_scooter, update_scooter, delete_scooter, search_scooters
from services.travellerCRUD import add_traveller, update_traveller, delete_traveller, search_traveller

from backup_restore import create_backup, restore_backup
from logs import view_logs

def main_menu(auth, conn):
    while True:
        if not auth.is_authenticated():
            print("\n=== URBAN MOBILITY LOGIN ===")
            if not auth.login():
                continue

        role = auth.get_current_user()["role"]

        print(f"\n=== MAIN MENU ({role.upper()}) ===")
        print("1. Search scooter")
        print("2. Update scooter")

        if auth.can("create_scooter"):
            print("3. Add new scooter")
        if auth.can("delete_scooter"):
            print("4. Delete scooter")

        if auth.can("add_traveller"):
            print("5. Add new traveller")
        if auth.can("update_traveller"):
            print("6. Update traveller")
        if auth.can("delete_traveller"):
            print("7. Delete traveller")
        if auth.can("search_traveller"):
            print("8. Search traveller")

        if auth.can("create_engineer") or auth.can("create_sysadmin"):
            print("9. Manage users (engineers/sysadmins)")

        if auth.can("view_logs"):
            print("10. View logs")

        if auth.can("create_backup"):
            print("11. Create backup")
        if auth.can("restore_backup"):
            print("12. Restore backup")

        print("L. Logout")
        print("X. Exit")

        choice = input("Choose an option: ").strip().lower()

        if choice == "1":
            search_scooters(conn, auth)
        elif choice == "2":
            update_scooter(conn, auth)
        elif choice == "3" and auth.can("create_scooter"):
            create_scooter(conn, auth)
        elif choice == "4" and auth.can("delete_scooter"):
            delete_scooter(conn, auth)
        elif choice == "5" and auth.can("add_traveller"):
            add_traveller(conn, auth)
        elif choice == "6" and auth.can("update_traveller"):
            update_traveller(conn, auth)
        elif choice == "7" and auth.can("delete_traveller"):
            delete_traveller(conn, auth)
        elif choice == "8" and auth.can("search_traveller"):
            search_traveller(conn, auth)
        elif choice == "9" and (auth.can("create_engineer") or auth.can("create_sysadmin")):
            auth.create_user()
        elif choice == "10" and auth.can("view_logs"):
            view_logs(conn, auth)
        elif choice == "11" and auth.can("create_backup"):
            create_backup(conn, auth)
        elif choice == "12" and auth.can("restore_backup"):
            restore_backup(conn, auth)
        elif choice == "l":
            auth.logout()
        elif choice == "x":
            print("Exiting system.")
            break
        else:
            print("Invalid choice or access denied.")

if __name__ == "__main__":
    try:
        conn = sqlite3.connect("urban_mobility.db")
        auth = UserAuthentication(conn)
        main_menu(auth, conn)
    except KeyboardInterrupt:
        print("\nSystem exited by user.")
    finally:
        conn.close()
