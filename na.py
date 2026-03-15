"""Admin utility: hash passwords and verify hashes using the same
HMAC-SHA256 scheme as the game server.
"""

import hashlib
import hmac
import os
import sys

from dotenv import load_dotenv

load_dotenv()

_AUTH_KEY = os.getenv("AUTH_SECRET_KEY", "").encode()


def hash_password(password: str) -> str:
    return hmac.new(_AUTH_KEY, password.encode(), hashlib.sha256).hexdigest()


def verify_hash(password: str, expected_hash: str) -> bool:
    return hmac.compare_digest(hash_password(password), expected_hash)


def main() -> None:
    if not _AUTH_KEY:
        print("Error: AUTH_SECRET_KEY is not set in .env")
        sys.exit(1)

    print("1) Password → Hash")
    print("2) Verify password against hash")
    choice = input("\nChoose [1/2]: ").strip()

    if choice == "1":
        password = input("Enter password: ")
        print(f"\nHash: {hash_password(password)}")

    elif choice == "2":
        password = input("Enter password: ")
        h = input("Enter hash:     ")
        if verify_hash(password, h):
            print("\nMatch — password is correct.")
        else:
            print("\nNo match — password is incorrect.")

    else:
        print("Invalid choice.")
        sys.exit(1)


if __name__ == "__main__":
    main()
