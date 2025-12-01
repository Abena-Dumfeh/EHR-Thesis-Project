import base64
import bcrypt
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

# AES Key must be exactly 32 bytes (AES-256)
AES_KEY = b'ThisIsASecretKey1234567890123456'

# 🔐 Encrypt a plaintext field using AES-256-CBC
def encrypt_field(plaintext):
    iv = get_random_bytes(16)
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    padded = pad(plaintext.encode(), AES.block_size)
    encrypted = cipher.encrypt(padded)
    return base64.b64encode(iv + encrypted).decode()

# 🔓 Decrypt an AES-encrypted field (used only by admin panel if needed)
#def decrypt_field(ciphertext_b64):
#    raw = base64.b64decode(ciphertext_b64)
#    iv = raw[:16]
#    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
#    decrypted = unpad(cipher.decrypt(raw[16:]), AES.block_size)
#    return decrypted.decode()

# 🔓 Decrypt an AES-encrypted field (e.g., encrypted_name)
def decrypt_field(ciphertext_b64):
    raw = base64.b64decode(ciphertext_b64)
    iv = raw[:16]
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(raw[16:]), AES.block_size)
    return decrypted.decode()

# 🔑 Hash a password using bcrypt
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# 🔍 Check password against hash
def check_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
