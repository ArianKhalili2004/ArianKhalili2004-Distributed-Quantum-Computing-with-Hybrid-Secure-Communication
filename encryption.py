"""Utility functions for AES encryption using bit-string keys."""

from Cryptodome.Cipher import AES  # pycryptodomex
from Cryptodome.Random import get_random_bytes

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
    """Encrypt ``plaintext`` with AES-GCM using ``key_bits``.

    The returned bytes contain the random nonce, ciphertext, and tag.
    """
    key = _bits_to_key(key_bits)
    nonce = get_random_bytes(12)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode())
    return nonce + ciphertext + tag

def decrypt_message_AES(key_bits: str, ciphertext: bytes) -> str:
    """Decrypt bytes produced by :func:`encrypt_message_AES`."""
    key = _bits_to_key(key_bits)
    nonce = ciphertext[:12]
    tag = ciphertext[-16:]
    data = ciphertext[12:-16]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    plain = cipher.decrypt_and_verify(data, tag)
    return plain.decode()
