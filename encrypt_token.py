#!/usr/bin/env python3
"""Encrypt/decrypt backup token"""

import base64
import sys

def simple_encrypt(plaintext: str, password: str) -> str:
    """Simple XOR-based encryption"""
    key = (password * (len(plaintext) // len(password) + 1))[:len(plaintext)]
    encrypted = bytearray()
    for i, char in enumerate(plaintext):
        encrypted.append(ord(char) ^ ord(key[i]))
    return base64.b64encode(bytes(encrypted)).decode()

def simple_decrypt(ciphertext: str, password: str) -> str:
    """Decrypt the token"""
    encrypted = base64.b64decode(ciphertext)
    key = (password * (len(encrypted) // len(password) + 1))[:len(encrypted)]
    decrypted = ''.join(chr(b ^ ord(key[i])) for i, b in enumerate(encrypted))
    return decrypted

PASSWORD = "kimi-backup-2026"
TOKEN = ".ay$[2^q(>,>^L'/3~m!k|NiQGuN_^mQK:|yGEt7"

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--decrypt":
        # Decrypt mode
        with open('github_backup_token.enc', 'r') as f:
            encrypted = f.read().strip()
        decrypted = simple_decrypt(encrypted, PASSWORD)
        print(f"Decrypted token: {decrypted}")
    else:
        # Encrypt mode
        encrypted = simple_encrypt(TOKEN, PASSWORD)
        with open('github_backup_token.enc', 'w') as f:
            f.write(encrypted)
        print("✅ Encrypted token saved to: github_backup_token.enc")
        print(f"\nTo decrypt:")
        print(f"  python encrypt_token.py --decrypt")
