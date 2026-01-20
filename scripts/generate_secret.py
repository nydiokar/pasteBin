#!/usr/bin/env python3
"""
Session secret generator for Paste Server
Generates cryptographically secure random key
"""
import secrets


def generate_secret_key(length: int = 64) -> str:
    """Generate cryptographically secure random key (hex format for Docker compatibility)"""
    return secrets.token_hex(length)


def main() -> None:
    print("=== Paste Server - Session Secret Generator ===\n")

    secret = generate_secret_key()

    print("[OK] Session secret generated!")
    print("\nAdd this to your deployment/.env file:")
    print("-" * 80)
    print(f"SESSION_SECRET={secret}")
    print("-" * 80)
    print("\n[WARNING] Keep this secret safe! Don't commit to git.")


if __name__ == '__main__':
    main()
