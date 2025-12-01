import os
import json
import subprocess
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# Paths
INPUT_PATH = '../files/sample_fhir_ehr.json'
OUTPUT_ENC_PATH = '../files/sample_fhir_ehr.json.aes'
KEY_PATH = '../keys/aes_key.bin'  # Store AES key here

def encrypt_file_aes(input_path, output_path, key_path):
    with open(input_path, 'rb') as f:
        data = f.read()

    key = get_random_bytes(32)  # AES-256 key
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data)

    with open(output_path, 'wb') as f:
        f.write(cipher.nonce + tag + ciphertext)

    # Save key (insecure demo — protect this key in production!)
    os.makedirs(os.path.dirname(key_path), exist_ok=True)
    with open(key_path, 'wb') as kf:
        kf.write(key)

    print(f"✅ AES encryption complete: {output_path}")

def upload_to_ipfs(filepath):
    try:
        result = subprocess.run(['ipfs', 'add', '-Q', filepath], capture_output=True, text=True, check=True)
        cid = result.stdout.strip().split()[-1]
        print(f"✅ Uploaded to IPFS: CID = {cid}")
        return cid
    except subprocess.CalledProcessError as e:
        print("❌ IPFS upload failed:", e.stderr)
        return None

if __name__ == "__main__":
    encrypt_file_aes(INPUT_PATH, OUTPUT_ENC_PATH, KEY_PATH)
    upload_to_ipfs(OUTPUT_ENC_PATH)
