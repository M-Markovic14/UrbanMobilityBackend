ROLE_PERMISSIONS = {
    "superadmin": {
        "create_scooter": True,
        "update_scooter": True,
        "delete_scooter": True,
        "search_scooter": True,

        "add_traveller": True,
        "update_traveller": True,
        "delete_traveller": True,
        "search_traveller": True,

        "create_sysadmin": True,
        "update_sysadmin": True,
        "delete_sysadmin": True,
        "reset_sysadmin_password": True,

        "create_engineer": True,
        "update_engineer": True,
        "delete_engineer": True,
        "reset_engineer_password": True,

        "view_logs": True,
        "generate_restore_code": True,
        "use_restore_code": False,  # only sysadmin can use the code
        "create_backup": True,
        "restore_backup": True
    },
    "sysadmin": {
        "create_scooter": True,
        "update_scooter": True,
        "delete_scooter": True,
        "search_scooter": True,

        "add_traveller": True,
        "update_traveller": True,
        "delete_traveller": True,
        "search_traveller": True,

        "create_sysadmin": False,
        "update_sysadmin": False,
        "delete_sysadmin": False,
        "reset_sysadmin_password": False,

        "create_engineer": True,
        "update_engineer": True,
        "delete_engineer": True,
        "reset_engineer_password": True,

        "view_logs": True,
        "generate_restore_code": False,
        "use_restore_code": True,   # only sysadmin may use code to restore
        "create_backup": True,
        "restore_backup": True
    },
    "engineer": {
        "create_scooter": False,
        "update_scooter": True,  # only allowed attributes must be checked elsewhere
        "delete_scooter": False,
        "search_scooter": True,

        "add_traveller": False,
        "update_traveller": False,
        "delete_traveller": False,
        "search_traveller": False,

        "create_sysadmin": False,
        "update_sysadmin": False,
        "delete_sysadmin": False,
        "reset_sysadmin_password": False,

        "create_engineer": False,
        "update_engineer": False,
        "delete_engineer": False,
        "reset_engineer_password": False,

        "view_logs": False,
        "generate_restore_code": False,
        "use_restore_code": False,
        "create_backup": False,
        "restore_backup": False
    }
}