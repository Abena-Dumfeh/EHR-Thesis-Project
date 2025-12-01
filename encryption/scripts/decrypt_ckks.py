import tenseal as ts

# Paths
context_path = "../keys/context_ckks.tenseal"   # adjust if needed
encrypted_file = "ckks_download.bin"

# Load context
with open(context_path, "rb") as f:
    context_bytes = f.read()
context = ts.context_from(context_bytes)
context.make_context_private()

# Load ciphertext
with open(encrypted_file, "rb") as f:
    encrypted_vector = ts.ckks_vector_from(context, f.read())

# Decrypt
decrypted = encrypted_vector.decrypt()
print("✅ CKKS decryption done. Decrypted values:")
print(decrypted)
