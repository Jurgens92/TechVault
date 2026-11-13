"""
Encryption service for sensitive data in TechVault.
Uses Fernet symmetric encryption (AES-128-CBC with HMAC).
"""
import base64
import os
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings


class EncryptionError(Exception):
    """Raised when encryption/decryption fails."""
    pass


class PasswordEncryption:
    """
    Handles encryption and decryption of passwords stored in the database.
    Uses Fernet (AES-128-CBC + HMAC-SHA256) for symmetric encryption.
    """

    # Prefix to identify encrypted values
    ENCRYPTED_PREFIX = "ENC::"

    def __init__(self):
        """Initialize with encryption key derived from Django's SECRET_KEY."""
        self._fernet = self._create_fernet()

    def _create_fernet(self):
        """Create a Fernet instance using a key derived from FIELD_ENCRYPTION_KEY."""
        # Use PBKDF2 to derive a proper encryption key from FIELD_ENCRYPTION_KEY
        # This ensures the key is the correct length and adds additional security
        secret_key = getattr(settings, 'FIELD_ENCRYPTION_KEY', settings.SECRET_KEY).encode()

        # Use a static salt derived from the app name
        # In production, this could be stored separately for additional security
        salt = b'TechVault_Password_Encryption_Salt_v1'

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret_key))
        return Fernet(key)

    def encrypt(self, plaintext: str, force: bool = False) -> str:
        """
        Encrypt a plaintext password.

        Args:
            plaintext: The password to encrypt
            force: Encrypt even if the value looks already encrypted. Use this for
                   user-supplied input, which is always plaintext - otherwise a
                   password that happens to start with the prefix would be stored
                   unencrypted and later fail to decrypt.

        Returns:
            Encrypted password with prefix

        Raises:
            EncryptionError: If encryption fails
        """
        if not plaintext:
            return plaintext

        # Don't double-encrypt values that came from storage
        if not force and self.is_encrypted(plaintext):
            return plaintext

        try:
            encrypted_bytes = self._fernet.encrypt(plaintext.encode('utf-8'))
            encrypted_str = base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')
            return f"{self.ENCRYPTED_PREFIX}{encrypted_str}"
        except Exception as e:
            raise EncryptionError(f"Failed to encrypt password: {str(e)}")

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt an encrypted password.

        Args:
            ciphertext: The encrypted password

        Returns:
            Decrypted password

        Raises:
            EncryptionError: If decryption fails
        """
        if not ciphertext:
            return ciphertext

        # If not encrypted, return as-is (for backwards compatibility)
        if not self.is_encrypted(ciphertext):
            return ciphertext

        try:
            # Remove prefix and decode
            encrypted_str = ciphertext[len(self.ENCRYPTED_PREFIX):]
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_str.encode('utf-8'))
            decrypted_bytes = self._fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except InvalidToken:
            raise EncryptionError("Failed to decrypt password: Invalid token or corrupted data")
        except Exception as e:
            raise EncryptionError(f"Failed to decrypt password: {str(e)}")

    def is_encrypted(self, value: str) -> bool:
        """Check if a value is already encrypted."""
        return bool(value) and value.startswith(self.ENCRYPTED_PREFIX)


# Singleton instance for use throughout the application
password_encryption = PasswordEncryption()


def encrypt_password(plaintext: str, force: bool = False) -> str:
    """Convenience function to encrypt a password (force=True for user input)."""
    return password_encryption.encrypt(plaintext, force=force)


def decrypt_password(ciphertext: str) -> str:
    """Convenience function to decrypt a password."""
    return password_encryption.decrypt(ciphertext)


def is_encrypted(value: str) -> bool:
    """Convenience function to check if a value is encrypted."""
    return password_encryption.is_encrypted(value)


def _derive_fernet_from_key(key_material: str) -> Fernet:
    """Derive a Fernet instance from arbitrary key material."""
    salt = b'TechVault_Password_Encryption_Salt_v1'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(key_material.encode()))
    return Fernet(key)


def protect_encryption_key(backup_password: str) -> dict:
    """
    Encrypt the current FIELD_ENCRYPTION_KEY with a user-provided backup password.
    Returns a dict to embed in the backup file.
    """
    encryption_key = getattr(settings, 'FIELD_ENCRYPTION_KEY', settings.SECRET_KEY)
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200000,
    )
    fernet = Fernet(base64.urlsafe_b64encode(kdf.derive(backup_password.encode())))
    encrypted_key = fernet.encrypt(encryption_key.encode())
    return {
        'salt': base64.urlsafe_b64encode(salt).decode(),
        'encrypted_key': base64.urlsafe_b64encode(encrypted_key).decode(),
    }


def recover_encryption_key(backup_password: str, key_data: dict) -> str:
    """
    Recover the original FIELD_ENCRYPTION_KEY from a backup using the backup password.
    Returns the original encryption key string.
    """
    salt = base64.urlsafe_b64decode(key_data['salt'].encode())
    encrypted_key = base64.urlsafe_b64decode(key_data['encrypted_key'].encode())
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200000,
    )
    fernet = Fernet(base64.urlsafe_b64encode(kdf.derive(backup_password.encode())))
    try:
        return fernet.decrypt(encrypted_key).decode()
    except InvalidToken:
        raise EncryptionError("Incorrect backup password")


def re_encrypt_value(ciphertext: str, old_key: str) -> str:
    """
    Decrypt a value with the old encryption key and re-encrypt with the current key.
    Returns the re-encrypted value, or the original if it's not encrypted.
    """
    if not ciphertext or not password_encryption.is_encrypted(ciphertext):
        return ciphertext

    prefix = PasswordEncryption.ENCRYPTED_PREFIX
    encrypted_str = ciphertext[len(prefix):]
    encrypted_bytes = base64.urlsafe_b64decode(encrypted_str.encode('utf-8'))

    # Decrypt with old key
    old_fernet = _derive_fernet_from_key(old_key)
    try:
        plaintext = old_fernet.decrypt(encrypted_bytes).decode('utf-8')
    except InvalidToken:
        raise EncryptionError("Failed to re-encrypt: old key does not match encrypted data")

    # Re-encrypt with current key
    return password_encryption.encrypt(plaintext)


def _password_fernet(password: str, salt: bytes) -> Fernet:
    """Derive a Fernet key from a user-supplied password and a random salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200000,
    )
    return Fernet(base64.urlsafe_b64encode(kdf.derive(password.encode())))


def encrypt_with_password(data: bytes, password: str) -> dict:
    """
    Encrypt arbitrary bytes with a password (used to protect sensitive sections
    of backup files, e.g. user password hashes and 2FA secrets).
    """
    salt = os.urandom(16)
    token = _password_fernet(password, salt).encrypt(data)
    return {
        'salt': base64.urlsafe_b64encode(salt).decode(),
        'data': token.decode(),
    }


def decrypt_with_password(payload: dict, password: str) -> bytes:
    """Reverse of encrypt_with_password. Raises EncryptionError on a wrong password."""
    try:
        salt = base64.urlsafe_b64decode(payload['salt'].encode())
        return _password_fernet(password, salt).decrypt(payload['data'].encode())
    except InvalidToken:
        raise EncryptionError("Incorrect backup password")
    except (KeyError, ValueError, TypeError, AttributeError):
        raise EncryptionError("Backup file is corrupted")


def can_decrypt(ciphertext: str) -> bool:
    """True if the value is plaintext or can be decrypted with the current key."""
    try:
        password_encryption.decrypt(ciphertext)
        return True
    except EncryptionError:
        return False
