import subprocess
import os
import tenseal as ts

# === Config ===
CID = input("Enter the CKKS IPFS CID: ").strip()
DOWNLOAD_PATH = '../files/downloaded.ckks.bin'
CONTEXT_PATH = '../files/context.ckks.tenseal'

def download_from_ipfs(cid, output_path):
    try:
        subprocess.run(['ipfs', 'get', cid, '-o', output_path], check=True)
        print(f"✅ Downloaded CKKS file from IPFS to {output_path}")
    except subprocess.CalledProcessError as e:
        print("❌ Failed to download from IPFS:", e)
        exit(1)

def decrypt_ckks(enc_path, ctx_path):
    with open(ctx_path, 'rb') as f:
        context = ts.context_from(f.read())

    with open(enc_path, 'rb') as f:
        encrypted_data = f.read()

    decrypted_vector = ts.ckks_vector_from(context, encrypted_data)
    print("✅ Decrypted CKKS values:")
    print([round(v, 2) for v in decrypted_vector.decrypt()])

if __name__ == "__main__":
    download_from_ipfs(CID, DOWNLOAD_PATH)
    decrypt_ckks(DOWNLOAD_PATH, CONTEXT_PATH)
