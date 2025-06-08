"""Utility functions for AES encryption using bit-string keys."""

from Cryptodome.Cipher import AES  # pycryptodomex

def _pkcs7_pad(data: bytes, block: int = 16) -> bytes:
    """Apply PKCS7 padding."""
    pad_len = block - len(data) % block
    return data + bytes([pad_len]) * pad_len

def _pkcs7_unpad(data: bytes) -> bytes:
    """Remove PKCS7 padding."""
    pad_len = data[-1]
    return data[:-pad_len]

def _bits_to_key(key_bits: str) -> bytes:
    """Convert a string of ``0`` and ``1`` into a 16-byte AES key."""
    if len(key_bits) % 8:
        key_bits += '0' * (8 - len(key_bits) % 8)
    key = int(key_bits, 2).to_bytes(len(key_bits) // 8, 'big')
    return (key + b'\x00' * 16)[:16]  # exactly 16 bytes

def encrypt_message_AES(key_bits: str, plaintext: str) -> bytes:
    """Encrypt ``plaintext`` with AES-ECB using ``key_bits``."""
    key = _bits_to_key(key_bits)
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.encrypt(_pkcs7_pad(plaintext.encode(), 16))

def decrypt_message_AES(key_bits: str, ciphertext: bytes) -> str:
    """Decrypt ``ciphertext`` with AES-ECB using ``key_bits``."""
    key = _bits_to_key(key_bits)
    cipher = AES.new(key, AES.MODE_ECB)
    plain = cipher.decrypt(ciphertext)
    return _pkcs7_unpad(plain).decode()
