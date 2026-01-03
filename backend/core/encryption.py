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
        """Create a Fernet instance using a key derived from SECRET_KEY."""
        # Use PBKDF2 to derive a proper encryption key from SECRET_KEY
        # This ensures the key is the correct length and adds additional security
        secret_key = settings.SECRET_KEY.encode()

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

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a plaintext password.

        Args:
            plaintext: The password to encrypt

        Returns:
            Encrypted password with prefix

        Raises:
            EncryptionError: If encryption fails
        """
        if not plaintext:
            return plaintext

        # Don't double-encrypt
        if self.is_encrypted(plaintext):
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
        return value and value.startswith(self.ENCRYPTED_PREFIX)


# Singleton instance for use throughout the application
password_encryption = PasswordEncryption()


def encrypt_password(plaintext: str) -> str:
    """Convenience function to encrypt a password."""
    return password_encryption.encrypt(plaintext)


def decrypt_password(ciphertext: str) -> str:
    """Convenience function to decrypt a password."""
    return password_encryption.decrypt(ciphertext)


def is_encrypted(value: str) -> bool:
    """Convenience function to check if a value is encrypted."""
    return password_encryption.is_encrypted(value)
