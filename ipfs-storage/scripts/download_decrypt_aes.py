import subprocess
import os
from Crypto.Cipher import AES

# === Config ===
CID = input("Enter the AES IPFS CID: ").strip()
#KEY_PATH = '../keys/aes_key.bin'
KEY_PATH = 'ipfs-storage/keys/aes_key.bin'
OUTPUT_PATH = 'ipfs-storage/files/decrypted_fhir_ehr.json'
ENC_FILE_PATH = 'ipfs-storage/files/downloaded.aes'
#OUTPUT_PATH = '../files/decrypted_fhir_ehr.json'
#ENC_FILE_PATH = '../files/downloaded.aes'

def download_from_ipfs(cid, output_path):
    try:
        subprocess.run(['ipfs', 'get', cid, '-o', output_path], check=True)
        print(f"✅ Downloaded encrypted file from IPFS to {output_path}")
    except subprocess.CalledProcessError as e:
        print("❌ Failed to download from IPFS:", e)
        exit(1)

def decrypt_file_aes(encrypted_path, key_path, output_path):
    with open(encrypted_path, 'rb') as f:
        nonce = f.read(16)
        tag = f.read(16)
        ciphertext = f.read()

    with open(key_path, 'rb') as kf:
        key = kf.read()

    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)

    with open(output_path, 'wb') as out:
        out.write(decrypted_data)

    print(f"✅ Decryption complete. Decrypted JSON saved to {output_path}")

if __name__ == "__main__":
    download_from_ipfs(CID, ENC_FILE_PATH)
    decrypt_file_aes(ENC_FILE_PATH, KEY_PATH, OUTPUT_PATH)
