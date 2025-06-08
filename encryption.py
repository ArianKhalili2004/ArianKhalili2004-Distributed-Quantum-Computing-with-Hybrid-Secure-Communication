# encryption.py  ─────────────────────────────────────────────

from Cryptodome.Cipher import AES      # pycryptodomex

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
    key = _bits_to_key(key_bits)
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.encrypt(_pkcs7_pad(plaintext.encode(), 16))

def decrypt_message_AES(key_bits: str, ciphertext: bytes) -> str:
    key = _bits_to_key(key_bits)
    cipher = AES.new(key, AES.MODE_ECB)
    plain = cipher.decrypt(ciphertext)
    return _pkcs7_unpad(plain).decode()
