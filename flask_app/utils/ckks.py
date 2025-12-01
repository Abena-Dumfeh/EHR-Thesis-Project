import tenseal as ts

def encrypt_ckks_vector(values):
    context = ts.context(
        ts.SCHEME_TYPE.CKKS,
        poly_modulus_degree=8192,
        coeff_mod_bit_sizes=[60, 40, 40, 60]
    )
    context.global_scale = 2**40
    context.generate_galois_keys()
    enc_vector = ts.ckks_vector(context, values)
    return enc_vector.serialize(), context.serialize(save_secret_key=True)

def save_ckks_context(context_bytes, file_path):
    with open(file_path, 'wb') as f:
        f.write(context_bytes)
