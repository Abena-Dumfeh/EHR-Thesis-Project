import os
import json
import tenseal as ts
import ipfshttpclient
from flask import Blueprint, request, render_template, redirect, url_for, flash

doctor_bp = Blueprint('doctor_bp', __name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Reuse the same TenSEAL context
context = ts.context(
    ts.SCHEME_TYPE.CKKS,
    poly_modulus_degree=8192,
    coeff_mod_bit_sizes=[60, 40, 40, 60]  # 128-bit security
)
context.global_scale = 2**40
context.generate_galois_keys()

# Connect to IPFS
ipfs = ipfshttpclient.connect("/ip4/127.0.0.1/tcp/5001")

@doctor_bp.route('/upload_vitals', methods=['GET', 'POST'])
def upload_vitals():
    if request.method == 'POST':
        ehr_id = request.form['ehr_id']
        patient_id = request.form['patient_id']
        bp = float(request.form['bp'])
        glucose = float(request.form['glucose'])
        cholesterol = float(request.form['cholesterol'])
        notes = request.form['notes']

        # 1. Save plaintext JSON
        plaintext_data = {
            "ehr_id": ehr_id,
            "patient_id": patient_id,
            "bp": bp,
            "glucose": glucose,
            "cholesterol": cholesterol,
            "notes": notes
        }

        plaintext_path = os.path.join(UPLOAD_FOLDER, f"{ehr_id}_plaintext.json")
        with open(plaintext_path, "w") as f:
            json.dump(plaintext_data, f)

        # 2. CKKS encrypt numeric values
        values = [bp, glucose, cholesterol]
        enc_vector = ts.ckks_vector(context, values)
        encrypted_bytes = enc_vector.serialize()

        ciphertext_path = os.path.join(UPLOAD_FOLDER, f"{ehr_id}_ckks.bin")
        with open(ciphertext_path, "wb") as f:
            f.write(encrypted_bytes)

        # 3. Upload to IPFS
        res = ipfs.add(ciphertext_path)
        ipfs_cid = res['Hash']

        # 4. Compare and display sizes (for thesis screenshot)
        plaintext_size = os.path.getsize(plaintext_path)
        ciphertext_size = os.path.getsize(ciphertext_path)

        print(f"Plaintext size: {plaintext_size} bytes")
        print(f"Ciphertext size: {ciphertext_size} bytes")
        print(f"IPFS CID: {ipfs_cid}")

        # Optional: Save metadata in DB or Fabric
        # insert_into_db(ehr_id, patient_id, ipfs_cid, plaintext_size, ciphertext_size)

        flash(f"Vital signs uploaded successfully. IPFS CID: {ipfs_cid}", "success")
        return redirect(url_for('doctor_bp.dashboard'))

    return render_template("upload_homo.html")
