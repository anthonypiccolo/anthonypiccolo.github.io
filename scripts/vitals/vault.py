"""Garmin session tokens, encrypted at rest.

The tokens live (encrypted) on the public `vitals` branch so the scheduled
workflow can save refreshed tokens after each run. The Fernet key that
decrypts them is only ever a GitHub Actions secret (VITALS_KEY) and a local
0600 file — never committed.
"""

import os
from pathlib import Path

from cryptography.fernet import Fernet

KEY_FILE = Path.home() / ".config" / "anthonypiccolo-vitals" / "key"


def load_key() -> bytes:
    key = os.environ.get("VITALS_KEY")
    if key:
        return key.encode()
    return KEY_FILE.read_bytes().strip()


def read_tokens(path: Path, key: bytes) -> str:
    return Fernet(key).decrypt(path.read_bytes()).decode()


def write_tokens(path: Path, key: bytes, tokens: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(Fernet(key).encrypt(tokens.encode()))
