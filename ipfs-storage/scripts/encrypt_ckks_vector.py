# encrypt_ckks_vector.py
import tenseal as ts
import json

def encrypt_ckks_vector(values):
    context = ts.context(
        ts.SCHEME_TYPE.CKKS,
        poly_modulus_degree=8192,  # ~128-bit security
        coeff_mod_bit_sizes=[60, 40, 40, 60]
    )
    context.generate_galois_keys()
    context.global_scale = 2**40

    ckks_vector = ts.ckks_vector(context, values)
    return ckks_vector.serialize(), context.serialize()

# Example use:
data = [123.0, 80.5, 65.7]
ciphertext, context = encrypt_ckks_vector(data)

with open("encrypted.ckks", "wb") as f:
    f.write(ciphertext)
with open("context.tenseal", "wb") as f:
    f.write(context)
