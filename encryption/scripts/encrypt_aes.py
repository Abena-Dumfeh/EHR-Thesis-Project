from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import os

output_path = '../output/aes_encrypted_data.bin'

# Generate a random 256-bit AES key
key = get_random_bytes(32)
cipher = AES.new(key, AES.MODE_EAX)

# Read the EHR file to encrypt
with open('../input/ehr_patient_record.pdf', 'rb') as f:
    data = f.read()

# Encrypt and digest
ciphertext, tag = cipher.encrypt_and_digest(data)

# Write encrypted data: nonce + tag + ciphertext
with open(output_path, 'wb') as f:
    f.write(cipher.nonce + tag + ciphertext)

# Save the AES key
with open('../output/aes_key.bin', 'wb') as kf:
    kf.write(key)

# ✅ Now check the file size AFTER it's written
size_bytes = os.path.getsize(output_path)
print("✅ AES encryption done")
print(f"🔐 Ciphertext size (AES): {size_bytes} bytes")
