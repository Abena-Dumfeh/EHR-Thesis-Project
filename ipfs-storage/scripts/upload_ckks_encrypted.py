import json
import re
import os
import subprocess
import tenseal as ts

# === Config ===
FHIR_PATH = '../files/sample_fhir_ehr.json'
CKKS_BIN_PATH = '../files/encrypted_values.ckks.bin'
CONTEXT_PATH = '../files/context.ckks.tenseal'

def extract_numbers_from_fhir(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    numbers = [float(n) for n in re.findall(r'\b\d+(?:\.\d+)?\b', json.dumps(data))]
    return numbers

def encrypt_ckks(numbers, enc_path, ctx_path):
    context = ts.context(
        ts.SCHEME_TYPE.CKKS,
        poly_modulus_degree=8192,
        coeff_mod_bit_sizes=[60, 40, 40, 60]
    )
    context.generate_galois_keys()
    context.global_scale = 2**40

    enc_vector = ts.ckks_vector(context, numbers)

    with open(enc_path, 'wb') as f:
        f.write(enc_vector.serialize())

    with open(ctx_path, 'wb') as f:
        f.write(context.serialize(save_secret_key=True))

    print(f"✅ CKKS encryption complete: {enc_path}")
    print(f"🧠 Context saved to: {ctx_path}")

def upload_to_ipfs(filepath):
    try:
        result = subprocess.run(['ipfs', 'add', '-Q', filepath], capture_output=True, text=True, check=True)
        cid = result.stdout.strip()
        print(f"✅ Uploaded to IPFS: CID = {cid}")
        return cid
    except subprocess.CalledProcessError as e:
        print("❌ IPFS upload failed:", e.stderr)
        return None

if __name__ == "__main__":
    numbers = extract_numbers_from_fhir(FHIR_PATH)
    if not numbers:
        print("⚠️ No numeric values found in FHIR file.")
        exit(0)

    encrypt_ckks(numbers, CKKS_BIN_PATH, CONTEXT_PATH)
    upload_to_ipfs(CKKS_BIN_PATH)
