import tenseal as ts
import pickle
import json

# Sample extracted values from PDF
bp = 118.0
glucose = 85.0
cholesterol = 175.0
vector = [bp, glucose, cholesterol]

context = ts.context(ts.SCHEME_TYPE.CKKS, poly_modulus_degree=8192, coeff_mod_bit_sizes=[60, 40, 40, 60])
context.global_scale = 2 ** 40
context.generate_galois_keys()

enc_vector = ts.ckks_vector(context, vector)
enc_bytes = enc_vector.serialize()

with open("ehr_patient_record_ckks.enc", "wb") as f:
    f.write(enc_bytes)

with open("ehr_ckks_context.tenseal", "wb") as f:
    f.write(context.serialize(save_public_key=True, save_secret_key=True, save_galois_keys=True))

print("CKKS Encrypted vector saved.")
