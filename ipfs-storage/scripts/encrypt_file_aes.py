from cryptography.fernet import Fernet
import sys
import os

def generate_key():
    key = Fernet.generate_key()
    with open("aes.key", "wb") as key_file:
        key_file.write(key)
    return key

def load_key():
    if not os.path.exists("aes.key"):
        return generate_key()
    with open("aes.key", "rb") as key_file:
        return key_file.read()

def encrypt_file(input_file):
    key = load_key()
    fernet = Fernet(key)

    with open(input_file, "rb") as f:
        data = f.read()

    encrypted = fernet.encrypt(data)

    encrypted_path = input_file + ".enc"
    with open(encrypted_path, "wb") as f:
        f.write(encrypted)

    print(f"✅ AES encryption complete: {encrypted_path}")
    return encrypted_path

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python encrypt_file_aes.py <file_to_encrypt>")
        sys.exit(1)

    file_to_encrypt = sys.argv[1]
    if not os.path.isfile(file_to_encrypt):
        print(f"❌ File not found: {file_to_encrypt}")
        sys.exit(1)

    encrypt_file(file_to_encrypt)
