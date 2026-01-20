#!/usr/bin/env python3
"""
Password hash generator for Paste Server
Generates bcrypt hash that goes into .env file
"""
import sys
import bcrypt
from getpass import getpass


def generate_password_hash(password: str) -> str:
    """Generate bcrypt hash from password"""
    salt: bytes = bcrypt.gensalt(rounds=12)
    hash_bytes: bytes = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hash_bytes.decode('utf-8')


def main() -> None:
    print("=== Paste Server - Password Setup ===\n")

    if len(sys.argv) > 1:
        # Password provided as argument (for scripting)
        password = sys.argv[1]
    else:
        # Interactive mode
        password = getpass("Enter password: ")
        password_confirm = getpass("Confirm password: ")

        if password != password_confirm:
            print("[ERROR] Passwords don't match!")
            sys.exit(1)

    if len(password) < 8:
        print("[ERROR] Password must be at least 8 characters!")
        sys.exit(1)

    print("\nGenerating hash...")
    password_hash = generate_password_hash(password)

    print("\n[OK] Password hash generated!")
    print("\nAdd this to your deployment/.env file:")
    print("-" * 60)
    print(f"PASSWORD_HASH='{password_hash}'")
    print("-" * 60)
    print("\nNote: Single quotes prevent shell/Docker from interpreting $ symbols")


if __name__ == '__main__':
    main()
