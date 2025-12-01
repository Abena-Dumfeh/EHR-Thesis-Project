from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import os

def pad(data):
    return data + b'\0' * (AES.block_size - len(data) % AES.block_size)

def encrypt_file_aes(filepath):
    key = get_random_bytes(32)  # AES-256
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)

    with open(filepath, 'rb') as f:
        data = f.read()
    padded_data = pad(data)
    encrypted_data = cipher.encrypt(padded_data)

    enc_path = filepath.replace(".pdf", "_aes.enc")
    with open(enc_path, 'wb') as f:
        f.write(iv + encrypted_data)

    key_path = filepath.replace(".pdf", "_aes.key")
    with open(key_path, 'wb') as f:
        f.write(key)

    print(f"AES Encrypted File: {enc_path}")
    print(f"AES Key File: {key_path}")
    return enc_path, key_path

encrypt_file_aes("ehr_patient_record.pdf")
