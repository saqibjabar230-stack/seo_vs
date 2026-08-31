import os
import base64
import hashlib


def _is_production() -> bool:
    return os.getenv("APP_ENV", "development").strip().lower() in {"production", "prod"}


def _get_derived_key() -> bytes:
    secret = os.getenv("SECRET_KEY")
    if not secret:
        if _is_production():
            raise RuntimeError("SECRET_KEY must be set in production. Refusing to start without a secret key.")
        secret = "seo_automation_local_dev_secret_key"
    return hashlib.sha256(secret.encode('utf-8')).digest()

def encrypt_credential(plain_text: str) -> str:
    """Simple XOR-CTR stream cipher with random nonce using hashlib SHA-256 for zero-dependency AES alternative."""
    if not plain_text:
        return ""
    key = _get_derived_key()
    nonce = os.urandom(16)
    keystream = hashlib.sha256(key + nonce).digest()
    plain_bytes = plain_text.encode('utf-8')
    cipher_bytes = bytearray()
    for i, b in enumerate(plain_bytes):
        cipher_bytes.append(b ^ keystream[i % len(keystream)])
    token = nonce + bytes(cipher_bytes)
    return "enc:" + base64.urlsafe_b64encode(token).decode('ascii')

def decrypt_credential(cipher_text: str) -> str:
    if not cipher_text:
        return ""
    if not cipher_text.startswith("enc:"):
        # Unencrypted plain text legacy credential
        return cipher_text
    try:
        raw = base64.urlsafe_b64decode(cipher_text[4:].encode('ascii'))
        if len(raw) <= 16:
            return ""
        nonce = raw[:16]
        cipher_bytes = raw[16:]
        key = _get_derived_key()
        keystream = hashlib.sha256(key + nonce).digest()
        plain_bytes = bytearray()
        for i, b in enumerate(cipher_bytes):
            plain_bytes.append(b ^ keystream[i % len(keystream)])
        return plain_bytes.decode('utf-8')
    except Exception:
        return ""
