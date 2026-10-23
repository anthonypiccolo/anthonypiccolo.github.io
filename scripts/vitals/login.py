"""One-off: log in to Garmin Connect and save encrypted session tokens.

Run in your own terminal (it prompts for your password and MFA code):

    .venv/bin/python scripts/vitals/login.py

Writes vitals-data/tokens.enc and, the first time, generates the key at
~/.config/anthonypiccolo-vitals/key. Your password is never stored.
"""

import getpass
import sys
from pathlib import Path

from cryptography.fernet import Fernet
from garminconnect import Garmin

from vault import KEY_FILE, write_tokens

OUT = Path(__file__).resolve().parents[2] / "vitals-data" / "tokens.enc"


def main() -> None:
    email = input("Garmin email: ").strip()
    password = getpass.getpass("Garmin password: ")
    garmin = Garmin(email, password, prompt_mfa=lambda: input("MFA code: ").strip())
    garmin.login()

    if not KEY_FILE.exists():
        KEY_FILE.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        KEY_FILE.write_bytes(Fernet.generate_key())
        KEY_FILE.chmod(0o600)

    write_tokens(OUT, KEY_FILE.read_bytes().strip(), garmin.client.dumps())
    print(f"Logged in as {garmin.get_full_name()}. Tokens saved to {OUT}")


if __name__ == "__main__":
    sys.exit(main())
