from cryptography.fernet import Fernet

def load_key():
    with open("secret.key", "rb") as f:
        return f.read()

fernet = Fernet(load_key())

def encrypt(text: str) -> str:
    return fernet.encrypt(text.encode()).decode()

def decrypt(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()
