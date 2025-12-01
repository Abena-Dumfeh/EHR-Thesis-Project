import argparse
import time
import tenseal as ts

parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True, help="Path to CKKS encrypted file")
parser.add_argument("--context", required=True, help="Path to CKKS context file")
args = parser.parse_args()

start_time = time.time()

# Load context with secret key
with open(args.context, "rb") as f:
    context = ts.context_from(f.read())

# Confirm context has secret key
if not context.is_private():
    print("❌ The loaded context does not have a secret key. Decryption will fail.")
    exit(1)

# Load encrypted data
with open(args.input, "rb") as f:
    encrypted = ts.ckks_vector_from(context, f.read())

# Decrypt
decrypted = encrypted.decrypt()

end_time = time.time()

# Output
print("✅ CKKS decryption done")
print("🔓 Decrypted values:", decrypted)
print(f"⏱️ Decryption time: {end_time - start_time:.4f} seconds")

