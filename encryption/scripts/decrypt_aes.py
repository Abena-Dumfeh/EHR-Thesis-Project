from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import json
import argparse

parser = argparse.ArgumentParser(description="AES File Decryption")
parser.add_argument('--input', required=True, help='Path to the encrypted file')
parser.add_argument('--key', required=True, help='Path to the AES key file')
parser.add_argument('--output', required=True, help='Path to save the decrypted output')
args = parser.parse_args()

# Load the AES key
with open(args.key, 'rb') as kf:
    key = kf.read()

# Read the encrypted file
with open(args.input, 'rb') as f:
    content = f.read()

# Extract nonce, tag, and ciphertext
nonce = content[:16]
tag = content[16:32]
ciphertext = content[32:]

# Decrypt
cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
plaintext = cipher.decrypt_and_verify(ciphertext, tag)

# Save decrypted file
with open(args.output, 'wb') as out:
    out.write(plaintext)

print("✅ AES decryption successful!")


