"""Argon2id password hashing shared by authentication and local fixtures."""

import secrets

from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError

password_hasher = PasswordHash.recommended()
# Unknown accounts still perform a password verification to reduce timing leakage.
_dummy_hash = password_hasher.hash(secrets.token_urlsafe(32))


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, stored_hash: str | None) -> bool:
    try:
        valid = password_hasher.verify(password, stored_hash or _dummy_hash)
    except UnknownHashError:
        password_hasher.verify(password, _dummy_hash)
        return False
    return stored_hash is not None and valid
