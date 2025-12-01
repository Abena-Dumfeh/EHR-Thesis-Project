import tenseal as ts
import json
import os

with open('../output/ehr_values.json') as f:
    data = json.load(f)
values = data['numeric_values']

context = ts.context(
    ts.SCHEME_TYPE.CKKS,
    poly_modulus_degree=16384,
    coeff_mod_bit_sizes=[60, 40, 40, 40, 60]  # ~2^128 security
)
context.global_scale = 2**40
context.generate_galois_keys()

enc = ts.ckks_vector(context, values)

with open("../output/ckks_encrypted_values.bin", "wb") as f:
    f.write(enc.serialize())
with open("../output/ckks_context.tenseal", "wb") as f:
    f.write(context.serialize(save_secret_key=True))

print("✅ CKKS encryption done")

# Size comparison
plaintext_size = sum(len(str(v)) for v in values)
ciphertext_size = os.path.getsize("../output/ckks_encrypted_values.bin")
print(f"🔢 Plaintext size: {plaintext_size} bytes")
print(f"🔐 Ciphertext size: {ciphertext_size} bytes")
