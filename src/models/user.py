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


@dataclass
class SuperAdmin(User):
    # Full access to all features; no password change
    def can_manage_system_admins(self) -> bool:
        return True

    def can_manage_service_engineers(self) -> bool:
        return True

    def can_manage_travellers(self) -> bool:
        return True

    def can_manage_scooters(self) -> bool:
        return True

    def can_view_logs(self) -> bool:
        return True

    def can_create_backup(self) -> bool:
        return True

    def can_restore_backup(self) -> bool:
        return True

    def can_generate_restore_code(self) -> bool:
        return True

    def can_revoke_restore_code(self) -> bool:
        return True

    def can_reset_passwords(self) -> bool:
        return True

    def can_update_password(self) -> bool:
        return False  # Hardcoded login


@dataclass
class SystemAdmin(User):
    def can_manage_service_engineers(self) -> bool:
        return True

    def can_manage_travellers(self) -> bool:
        return True

    def can_manage_scooters(self) -> bool:
        return True

    def can_view_logs(self) -> bool:
        return True

    def can_create_backup(self) -> bool:
        return True

    def can_restore_backup(self) -> bool:
        return True  # With valid restore code only

    def can_reset_passwords(self) -> bool:
        return True

    def can_update_own_profile(self) -> bool:
        return True

    def can_delete_own_account(self) -> bool:
        return True

    def can_update_password(self) -> bool:
        return True


@dataclass
class ServiceEngineer(User):
    def can_edit_scooter_fields(self) -> bool:
        return True  # Only specific fields

    def can_add_or_delete_scooter(self) -> bool:
        return False

    def can_manage_travellers(self) -> bool:
        return False

    def can_view_logs(self) -> bool:
        return False

    def can_update_password(self) -> bool:
        return True
