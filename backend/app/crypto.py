import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend


class CryptoManager:
    """
    AES-GCM encryption/decryption manager for API keys
    
    Uses a 256-bit key stored in ENCRYPTION_KEY_HEX environment variable.
    """
    
    def __init__(self):
        # Get encryption key from environment
        key_hex = os.getenv("ENCRYPTION_KEY_HEX")
        
        if not key_hex:
            raise ValueError("ENCRYPTION_KEY_HEX environment variable not set")
        
        # Convert hex to bytes (should be 32 bytes for AES-256)
        try:
            self.key = bytes.fromhex(key_hex)
        except ValueError:
            raise ValueError("ENCRYPTION_KEY_HEX must be a valid hex string")
        
        if len(self.key) != 32:
            raise ValueError("ENCRYPTION_KEY_HEX must be 32 bytes (64 hex characters) for AES-256")
        
        self.aesgcm = AESGCM(self.key)
    
    def encrypt(self, plaintext: str) -> tuple[str, str]:
        """
        Encrypt plaintext using AES-GCM
        
        Args:
            plaintext: String to encrypt
            
        Returns:
            Tuple of (ciphertext_hex, iv_hex)
        """
        # Generate a random 12-byte IV (nonce)
        iv = os.urandom(12)
        
        # Encrypt
        ciphertext = self.aesgcm.encrypt(iv, plaintext.encode(), None)
        
        # Return as hex strings
        return ciphertext.hex(), iv.hex()
    
    def decrypt(self, ciphertext_hex: str, iv_hex: str) -> str:
        """
        Decrypt ciphertext using AES-GCM
        
        Args:
            ciphertext_hex: Hex-encoded ciphertext
            iv_hex: Hex-encoded initialization vector
            
        Returns:
            Decrypted plaintext string
        """
        # Convert from hex
        ciphertext = bytes.fromhex(ciphertext_hex)
        iv = bytes.fromhex(iv_hex)
        
        # Decrypt
        plaintext_bytes = self.aesgcm.decrypt(iv, ciphertext, None)
        
        return plaintext_bytes.decode()


# Singleton instance
_crypto_manager = None


def get_crypto_manager() -> CryptoManager:
    """Get or create CryptoManager singleton"""
    global _crypto_manager
    
    if _crypto_manager is None:
        _crypto_manager = CryptoManager()
    
    return _crypto_manager
