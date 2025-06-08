# encryption.py  ─────────────────────────────────────────────

from Cryptodome.Cipher import AES      # pycryptodomex
from Cryptodome.Random import get_random_bytes

def _pkcs7_pad(data: bytes, block: int = 16) -> bytes:
    pad_len = block - len(data) % block
    return data + bytes([pad_len]) * pad_len

def _pkcs7_unpad(data: bytes) -> bytes:
    pad_len = data[-1]
    return data[:-pad_len]

def _bits_to_key(key_bits: str) -> bytes:
    if len(key_bits) % 8:
        key_bits += '0' * (8 - len(key_bits) % 8)
    key = int(key_bits, 2).to_bytes(len(key_bits)//8, 'big')
    return (key + b'\x00'*16)[:16]         # دقیقاً 16 بایت

def encrypt_message_AES(key_bits: str, plaintext: str) -> bytes:
    """Encrypt plaintext using AES-GCM with a random nonce.

    The returned bytes contain ``nonce || tag || ciphertext`` so that the
    caller can directly pass the result to :func:`decrypt_message_AES`.
    """
    key = _bits_to_key(key_bits)
    nonce = get_random_bytes(12)                 # recommended size for GCM
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode())
    return nonce + tag + ciphertext

def decrypt_message_AES(key_bits: str, ciphertext: bytes) -> str:
    """Decrypt data produced by :func:`encrypt_message_AES`. Raises an
    exception if authentication fails."""
    key = _bits_to_key(key_bits)
    nonce = ciphertext[:12]
    tag = ciphertext[12:28]
    ct = ciphertext[28:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    plain = cipher.decrypt_and_verify(ct, tag)
    return plain.decode()
