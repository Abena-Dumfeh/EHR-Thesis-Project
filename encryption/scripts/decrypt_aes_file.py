from Crypto.Cipher import AES
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True)
parser.add_argument('--key', required=True)
parser.add_argument('--output', required=True)
args = parser.parse_args()

# Read key
with open(args.key, 'rb') as kf:
    key = kf.read()

# Read encrypted data
with open(args.input, 'rb') as f:
    encrypted = f.read()

# Extract nonce, tag, and ciphertext
nonce = encrypted[:16]
tag = encrypted[16:32]
ciphertext = encrypted[32:]

# Decrypt
cipher = AES.new(key, AES.MODE_EAX, nonce)
plaintext = cipher.decrypt_and_verify(ciphertext, tag)

# Write decrypted output
with open(args.output, 'wb') as out:
    out.write(plaintext)

print("✅ AES decryption done")
