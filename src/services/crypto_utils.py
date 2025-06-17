from cryptography.fernet import Fernet
import os


def load_key():
    key_path = os.path.join(os.path.dirname(__file__), "secret.key")
    with open(key_path, "rb") as f:
        return f.read()

fernet = Fernet(load_key())

def encrypt(text: str) -> str:
    return fernet.encrypt(text.encode()).decode()

def decrypt(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()
