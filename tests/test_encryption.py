import sys, os
import pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from encryption import encrypt_message_AES, decrypt_message_AES


def test_encrypt_roundtrip():
    key = '1010101010101010'
    msg = 'hello world'
    ct = encrypt_message_AES(key, msg)
    pt = decrypt_message_AES(key, ct)
    assert pt == msg
