from cryptography.fernet import Fernet

from app.core.config import settings

# Initialize Fernet suite using settings encryption key
# Under validation rules, settings.ENCRYPTION_KEY is guaranteed to be a valid key
fernet = Fernet(settings.ENCRYPTION_KEY.encode())


def encrypt_token(token: str) -> str:
    """Encrypts a plaintext string token using symmetric Fernet encryption."""
    if not token:
        return ""
    encrypted_bytes = fernet.encrypt(token.encode("utf-8"))
    return encrypted_bytes.decode("utf-8")


def decrypt_token(encrypted_token: str) -> str:
    """Decrypts a Fernet encrypted string token back to plaintext."""
    if not encrypted_token:
        return ""
    decrypted_bytes = fernet.decrypt(encrypted_token.encode("utf-8"))
    return decrypted_bytes.decode("utf-8")
