import os
import re
import pdfplumber
import json
import ipfshttpclient
import tenseal as ts
import time
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
import mysql.connector
import subprocess
#from flask import request, redirect, render_template
#from utils.db import get_db_connection
#from utils.ipfs_client import get_ipfs_client
#from flask_app.doctor.upload import encrypt_file_aes
#from flask_app.doctor.upload import generate_vitals_fhir_json
#from flask_app.doctor.upload import encrypt_ckks_vector, save_ckks_context
from flask_app.doctor.upload import (
    convert_file_to_json,
    validate_fhir_json,
    encrypt_file_aes,
    extract_numbers_from_file,
    encrypt_ckks_vector,
    save_ckks_context
)
from flask_app.utils.db import get_db_connection
from flask_app.utils.ipfs_client import get_ipfs_client
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from werkzeug.utils import secure_filename

doctor_bp = Blueprint('doctor_bp', __name__, url_prefix='/doctor', template_folder='templates')
UPLOAD_FOLDER = 'temp_ehr'
bcrypt = Bcrypt()
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# IPFS client
ipfs = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

# DB connection
#db = mysql.connector.connect(
#    host="localhost",
#    user="ehruser",
#    password="StrongPass2025!",
#    database="ehrdb"
#)
#cursor = db.cursor(dictionary=True)


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="ehruser",
        password="StrongPass2025!",
        database="ehrdb"
    )

def extract_numbers_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    numbers = [float(n) for n in re.findall(r'\b\d+(?:\.\d+)?\b', content)]
    return numbers

def convert_file_to_json(original_path, record_type, receiver_type=None, notes=None, receiver_id=None):
    ext = os.path.splitext(original_path)[-1].lower()
    json_path = original_path + ".json"

    if ext == '.pdf':
        with pdfplumber.open(original_path) as pdf:
            text = '\n'.join(page.extract_text() or '' for page in pdf.pages)
    elif ext == '.txt':
        with open(original_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
    elif ext == '.json':
        return original_path  # Already structured
    else:
        raise ValueError("Unsupported file type. Please upload .pdf, .txt, or .json")

    # ✅ FHIR-compliant structure
    data = {
        "resourceType": "DocumentReference",
        "type": { "text": record_type },
        "subject": {"reference": f"{receiver_type}/{receiver_id or 'unknown'}"},
        "description": notes or "",
        "content": [{"attachment": {"contentType": "text/plain", "data": text}}]
    }

    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)

    return json_path

def encrypt_file_aes(input_path):
    with open(input_path, 'rb') as f:
        data = f.read()
    key = get_random_bytes(32)  # AES-256
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    output_path = input_path + '.aes'
    with open(output_path, 'wb') as f:
        f.write(cipher.nonce + tag + ciphertext)
    return output_path

def encrypt_numbers_ckks(numbers, output_path):
    context = ts.context(
        ts.SCHEME_TYPE.CKKS,
        poly_modulus_degree=8192,
        coeff_mod_bit_sizes=[60, 40, 40, 60]
    )
    context.global_scale = 2**40
    context.generate_galois_keys()

    enc_vector = ts.ckks_vector(context, numbers)
    with open(output_path, 'wb') as f:
        f.write(enc_vector.serialize())
    return output_path


@doctor_bp.route('/register', methods=['GET', 'POST'])
def register():
    # 🔹 Always load departments first
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT department_id, name FROM departments ORDER BY name ASC")
    departments = cursor.fetchall()

    if request.method == 'POST':
        name = request.form['name']
        department_id = request.form['department_id']
        email = request.form['email']
        contact = request.form['contact']
        password = request.form['password']

        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        cursor.execute("SELECT * FROM doctors WHERE email = %s", (email,))
        existing = cursor.fetchone()
        if existing:
            flash('Email already registered.', 'error')
            cursor.close()
            conn.close()
            return render_template('doctor/register.html', departments=departments)

        cursor.execute("""
            INSERT INTO doctors (name, email, contact, password_hash, department_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, email, contact, password_hash, department_id))

        conn.commit()
        cursor.close()
        conn.close()

        flash('Registration successful. Please log in.')
        return redirect(url_for('doctor_bp.login'))

    # ✅ Close connection and render GET page
    cursor.close()
    conn.close()
    return render_template('doctor/register.html', departments=departments)

@doctor_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM doctors WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and bcrypt.check_password_hash(user['password_hash'], password):
            session['doctor_id'] = user['doctor_id']
            session['doctor_name'] = user['name']
            flash('Login successful!', 'success')
            return redirect(url_for('doctor_bp.dashboard'))
        else:
            flash('Invalid email or password', 'error')

    return render_template('doctor/login.html')

@doctor_bp.route('/dashboard')
def dashboard():
    if 'doctor_id' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('doctor_bp.login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT ehr_key, record_type, created_at FROM ehr_records WHERE doctor_id = %s ORDER BY created_at DESC", (session['doctor_id'],))
    ehr_records = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('doctor/dashboard.html', name=session['doctor_name'], records=ehr_records)

@doctor_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('doctor_bp.login'))


@doctor_bp.route('/upload_ehr', methods=['GET', 'POST'])
def upload_ehr():
    if 'doctor_id' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('doctor_bp.login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
       #patient_id = request.form['patient_id']
        receiver_type = request.form['receiver_type']
        record_type = request.form['record_type']
        notes = request.form.get('notes', '').strip()
        ehr_key = f"ehr{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        doctor_id = session['doctor_id']
        created_at = datetime.utcnow()

# Determine receiver
        if receiver_type == 'patient':
            patient_id = request.form['patient_id']
            target_doctor_id = None
            doctor_dept = None
            consent_given = None
        elif receiver_type == 'doctor':
            target_doctor_id = request.form['target_doctor_id']
            doctor_dept = request.form['doctor_dept']
            consent_given = request.form.get('consent_given')
            if not consent_given:
                flash("❌ Patient consent is required for doctor-to-doctor sharing.", 'error')
                return redirect(request.url)
            patient_id = None  # patient might not be directly involved
        else:
            flash("❌ Invalid receiver type.", 'error')
            return redirect(request.url)

        uploaded_file = request.files['ehr_file']
        if uploaded_file.filename == '':
            flash('No file selected.', 'error')
            return redirect(request.url)

# Save uploaded file
        filename = secure_filename(uploaded_file.filename)
        original_path = os.path.join(UPLOAD_FOLDER, filename)
        uploaded_file.save(original_path)

# Convert to .json if needed
        try:
#            json_path = convert_file_to_json(original_path, record_type)
            json_path = convert_file_to_json(
                original_path,
                record_type,
                receiver_type=receiver_type,
                notes=notes,
                receiver_id=patient_id if receiver_type == 'patient' else target_doctor_id
             )

        except ValueError as e:
            flash(str(e), 'error')
            return redirect(request.url)


        # Validate FHIR JSON
        with open(json_path, 'r') as f:
            fhir_data = json.load(f)
        if not validate_fhir_json(fhir_data):
            flash("❌ FHIR validation failed.", "danger")
            return redirect(request.url)

        # Upload plaintext FHIR JSON to IPFS
        try:
            ipfs = get_ipfs_client()
            res_fhir = ipfs.add(json_path)
            fhir_cid = res_fhir['Hash']
        except Exception as e:
            flash(f"Failed to upload FHIR JSON: {str(e)}", "danger")
            return redirect(request.url)

        # AES encrypt FHIR JSON
        try:
            fhir_aes_path, _ = encrypt_file_aes(json_path)
            res_enc = ipfs.add(fhir_aes_path)
            fhir_enc_cid = res_enc['Hash']
        except Exception as e:
            flash(f"Failed to encrypt/upload FHIR JSON: {str(e)}", "danger")
            return redirect(request.url)

        # AES encryption of full file
        #aes_encrypted_path = encrypt_file_aes(json_path)
        #ipfs_cid = ipfs.add(aes_encrypted_path)['Hash']

        aes_encrypted_path = encrypt_file_aes(json_path)

        # ⏱️ Measure upload latency to IPFS
        start_upload = time.time()
        ipfs_cid = ipfs.add(aes_encrypted_path)['Hash']
        log_download_latency(ipfs_cid, ehr_key, "AES")
        end_upload = time.time()
        upload_latency = end_upload - start_upload

        encryption_type = 'AES' #initially default to AES

        # 📝 Log to CSV file
        with open("upload_times.csv", "a") as f:
            f.write(f"{ehr_key},{encryption_type},{upload_latency:.3f}\n")

        print(f"📤 Upload latency: {upload_latency:.3f} seconds")

        # Try to extract numbers and CKKS encrypt
        numbers = extract_numbers_from_file(json_path)
        if numbers:
            ckks_path = os.path.join(UPLOAD_FOLDER, f"{filename}.ckks.bin")
            ckks_encrypted_path = encrypt_numbers_ckks(numbers, ckks_path)
           # ckks_cid = client.add(ckks_encrypted_path)['Hash']
            ckks_cid = ipfs.add(ckks_encrypted_path)['Hash']
            log_download_latency(ckks_cid, ehr_key, "CKKS")
            encryption_type = 'Hybrid'

        else:
            ckks_cid = None  # no numbers to encrypt
            encryption_type = 'AES'

        # Store metadata in DB
        #encryption_type = 'Hybrid' 

        cursor.execute("""
            INSERT INTO ehr_records (
               ehr_key, patient_id, doctor_id, ipfs_cid, record_type, encryption_type, created_at, ckks_cid, target_doctor_id,
                doctor_dept, receiver_type, notes, fhir_cid, fhir_enc_cid
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (ehr_key, patient_id, doctor_id, ipfs_cid, record_type, encryption_type, created_at, ckks_cid, target_doctor_id, doctor_dept, receiver_type, notes, fhir_cid, fhir_enc_cid))

        conn.commit()
        cursor.close()
        conn.close()

        try:
            start_time = time.time()

            result = subprocess.run([
                "docker", "exec", "cli.doctororg.hospital1",
                "peer", "chaincode", "invoke",
                "-o", "orderer1.example.com:7050",
                "--ordererTLSHostnameOverride", "orderer1.example.com",
                "--tls",
                "--cafile", "/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer1.example.com/msp/tlscacerts/tlsca.example.com-cert.pem",
                "-C", "ehrchannel1",
                "-n", "ehr",
                "-c", json.dumps({
                    "Args": ["CreateEHRRecord", str (ehr_key), str ( patient_id )if patient_id else "", str ( record_type ) ,str ( ipfs_cid ), str ( ckks_cid ) if ckks_cid else "", str (fhir_cid), str (fhir_enc_cid), "true" if receiver_type == "doctor" and consent_given else "false"]
                }),
                "--peerAddresses", "peer0.doctororg.hospital1.com:10051",
                "--tlsRootCertFiles", "/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/doctororg.hospital1.com/peers/peer0.doctororg.hospital1.com/tls/ca.crt"
            ], check=True, capture_output=True, text=True)

            end_time = time.time()
            block_creation_time = end_time - start_time
            print(f"🕒 Block creation time: {block_creation_time:.3f} seconds")

             # Optional: save to CSV
            with open("block_times.csv", "a") as f:
                f.write(f"{ehr_key},{block_creation_time:.3f}\n")

            print("✅ Fabric invoke success:\n", result.stdout)

        except subprocess.CalledProcessError as e:
            print("❌ Fabric invoke failed:\n", e.stderr)
            flash(f"Blockchain invoke failed: {e.stderr}", 'error')
            return redirect(request.url)

        # Clean up temp files
        if os.path.exists(original_path):
            os.remove(original_path)
        if os.path.exists(aes_encrypted_path):
            os.remove(aes_encrypted_path)
        if ckks_cid and os.path.exists(ckks_path):
            os.remove(ckks_path)


        flash(f"EHR uploaded successfully. AES CID: {ipfs_cid}" + (f", CKKS CID: {ckks_cid}" if ckks_cid else ""), 'success')
        print("✅ Redirecting to dashboard after successful upload")
        return redirect(url_for('doctor_bp.dashboard'))

       #GET: Load patients
    cursor.execute("SELECT patient_id, name, email FROM patients")
    patients = cursor.fetchall()

    cursor.execute("SELECT name FROM departments ORDER BY name ASC")
    departments = [row['name'] for row in cursor.fetchall()]

    cursor.execute("SELECT doctor_id, name, email FROM doctors WHERE doctor_id != %s", (session['doctor_id'],))
    doctors = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('doctor/upload_ehr.html', patients=patients, departments=departments, doctors=doctors)

@doctor_bp.route('/ehr_overview')
def ehr_overview():
    if 'doctor_id' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('doctor_bp.login'))

    doctor_id = session['doctor_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 1. Records sent to patients
    cursor.execute("""
        SELECT ehr_key, patient_id, record_type, notes, created_at 
        FROM ehr_records 
        WHERE doctor_id = %s AND receiver_type = 'patient'
        ORDER BY created_at DESC
    """, (doctor_id,))
    sent_to_patients = cursor.fetchall()

    # 2. Records received from another doctor
    cursor.execute("""
        SELECT ehr_key, target_doctor_id, doctor_dept, record_type, notes, created_at 
        FROM ehr_records 
        WHERE target_doctor_id = %s AND receiver_type = 'doctor'
        ORDER BY created_at DESC
    """, (doctor_id,))
    received_from_doctors = cursor.fetchall()

    # 3. Records shared by this doctor (based on consent given)
    cursor.execute("""
        SELECT ehr_key, patient_id, target_doctor_id, record_type, notes, created_at 
        FROM ehr_records 
        WHERE doctor_id = %s AND receiver_type = 'doctor' AND target_doctor_id IS NOT NULL
        ORDER BY created_at DESC
    """, (doctor_id,))
    shared_records = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("doctor/ehr_overview.html",
                           sent_to_patients=sent_to_patients,
                           received_from_doctors=received_from_doctors,
                           shared_records=shared_records)

@doctor_bp.route('/view_ehr/<ehr_key>')
def view_ehr(ehr_key):
    if 'doctor_id' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('doctor_bp.login'))

    try:
        result = subprocess.run([
            "docker", "exec", "cli.doctororg.hospital1",
            "peer", "chaincode", "query",
            "-C", "ehrchannel1",
            "-n", "ehr",
            "-c", json.dumps({
                "Args": ["ReadEHRRecord", ehr_key]
            })
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)

        record_json = result.stdout.strip()
        ehr_record = json.loads(record_json)

        return render_template('doctor/view_ehr.html', ehr=ehr_record)

    except subprocess.CalledProcessError as e:
        flash(f"❌ Failed to fetch record: {e.stderr.strip()}", 'error')
        return redirect(url_for('doctor_bp.dashboard'))
    except json.JSONDecodeError:
        flash("❌ Failed to decode blockchain response", 'error')
        return redirect(url_for('doctor_bp.dashboard'))


@doctor_bp.route('/upload_homo', methods=['GET', 'POST'])
def upload_homo():
    if 'doctor_id' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('doctor_bp.login'))

    if request.method == 'POST':
        ehr_key = f"ehr{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        patient_id = request.form['patient_id']
        doctor_id = session['doctor_id']
        bp = float(request.form['bp'])
        glucose = float(request.form['glucose'])
        cholesterol = float(request.form['cholesterol'])
        notes = request.form.get('notes', '')

        # Step 1: Generate FHIR JSON
        from flask_app.doctor.upload import generate_vitals_fhir_json, validate_fhir_json
        fhir_json_path = generate_vitals_fhir_json(ehr_key, patient_id, bp, glucose, cholesterol, notes)

        # Step 2: Validate FHIR JSON
        with open(fhir_json_path, 'r') as f:
            fhir_data = json.load(f)
        if not validate_fhir_json(fhir_data):
            flash("❌ Invalid FHIR format. Upload failed.", "danger")
            return render_template('doctor/upload_homo.html')

        # Step 3: Upload FHIR JSON to IPFS
        try:
            from flask_app.utils.ipfs_client import get_ipfs_client
            ipfs = get_ipfs_client()
            res_fhir = ipfs.add(fhir_json_path)
            fhir_cid = res_fhir['Hash']
        except Exception as e:
            flash(f"IPFS upload of FHIR JSON failed: {str(e)}", "danger")
            return render_template('doctor/upload_homo.html')

# Step 3b: AES-encrypt the FHIR JSON
        try:
            fhir_aes_path, _ = encrypt_file_aes(fhir_json_path)
        except Exception as e:
            flash(f"Encryption of FHIR JSON failed: {str(e)}", "danger")
            return render_template('doctor/upload_homo.html')

# Step 3c: Upload AES-encrypted FHIR JSON to IPFS
        try:
            res_fhir_enc = ipfs.add(fhir_aes_path)
            fhir_enc_cid = res_fhir_enc['Hash']
        except Exception as e:
            flash(f"Upload of AES-encrypted FHIR JSON failed: {str(e)}", "danger")
            return render_template('doctor/upload_homo.html')


        # Step 4: CKKS encryption
        from flask_app.doctor.upload import encrypt_ckks_vector, save_ckks_context
        ehr_vector = [bp, glucose, cholesterol]
        encrypted_data, context_bytes = encrypt_ckks_vector(ehr_vector)

        ehr_filename = f"{ehr_key}_vitals.ckks"
        context_filename = f"{ehr_key}_context.tenseal"
        ehr_bin_path = f"./files/{ehr_filename}"
        context_path = f"./keys/{context_filename}"

        with open(ehr_bin_path, 'wb') as f:
            f.write(encrypted_data)
        save_ckks_context(context_bytes, context_path)

        # Step 5: Upload CKKS to IPFS
        #try:
        #    res_ckks = ipfs.add(ehr_bin_path)
        #    ckks_cid = res_ckks['Hash']
        #except Exception as e:
        #    flash(f"IPFS upload of CKKS failed: {str(e)}", "danger")
        #    return render_template('doctor/upload_homo.html')

        try:
            start_upload = time.time()
            res_ckks = ipfs.add(ehr_bin_path)
            end_upload = time.time()

            ckks_cid = res_ckks['Hash']
            log_download_latency(ckks_cid, ehr_key, "CKKS")
            upload_latency = end_upload - start_upload

          # 📝 Log upload latency to CSV
            with open("upload_times.csv", "a") as f:
                f.write(f"{ehr_key},CKKS,{upload_latency:.3f}\n")

            print(f"📤 CKKS Upload latency: {upload_latency:.3f} seconds")

        except Exception as e:
            flash(f"IPFS upload of CKKS failed: {str(e)}", "danger")
            return render_template('doctor/upload_homo.html')


        # Step 6: Save metadata in SQL
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO ehr_records (
                    ehr_key, doctor_id, patient_id, ehr_type, ckks_cid, fhir_cid, fhir_enc_cid, notes, encryption_type, receiver_type
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (ehr_key, doctor_id, patient_id, 'vitals', ckks_cid, fhir_cid, fhir_enc_cid, notes, 'CKKS', 'patient'))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            flash(f"MySQL insert failed: {str(e)}", "danger")
            return render_template('doctor/upload_homo.html')

        # Step 7: Invoke Fabric chaincode
        try:
            start_time = time.time()

            result = subprocess.run([
                "docker", "exec", "cli.doctororg.hospital1.com", "peer", "chaincode", "invoke",
                "-o", "orderer.example.com:7050",
                "--tls", "--cafile", "/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem",
                "-C", "ehrchannel1",
                "-n", "ehr",
                "-c", json.dumps({
                    "Args": ["CreateEHRRecord", str ( ehr_key ), str ( patient_id ), "doctororg.hospital1.com", "CKKS", str ( ckks_cid )]
                })
            ], capture_output=True, text=True, check=True)

            end_time = time.time()
            block_creation_time = end_time - start_time
            print(f"🕒 Block creation time: {block_creation_time:.3f} seconds")

               # Optional: save to CSV
            with open("block_times.csv", "a") as f:
                f.write(f"{ehr_key},{block_creation_time:.3f}\n")

            print("✅ Chaincode invoked successfully")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)

        except subprocess.CalledProcessError as e:
            print("❌ Chaincode invoke failed")
            print("STDERR:", e.stderr)
            flash(f"Chaincode invoke failed: {e.stderr}", "danger")
            return render_template('doctor/upload_homo.html')

        flash("✅ Vital signs uploaded and secured!", "success")
        return redirect(url_for('doctor_bp.dashboard'))

    # GET: Load patient list
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT patient_id, name, email FROM patients")
    patients = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('doctor/upload_homo.html', patients=patients)
    # GET: Load patients
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT patient_id, name, email FROM patients")
    patients = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('doctor/upload_homo.html', patients=patients)

@doctor_bp.route('/test_download_latency/<cid>')
def test_download_latency(cid):
    try:
        start_download = time.time()
        data = ipfs.cat(cid)
        end_download = time.time()
        download_latency = end_download - start_download

        with open("download_times.csv", "a") as f:
            f.write(f"{cid},Unknown,{download_latency:.3f}\n")

        return f"Download latency: {download_latency:.3f} seconds"
    except Exception as e:
        return f"Failed to download from IPFS: {e}"
    
    # 🆕 Inline download latency measurement to use after IPFS uploads

def log_download_latency(cid, ehr_key, label):
    try:
        start_download = time.time()
        ipfs.cat(cid)
        end_download = time.time()
        download_latency = end_download - start_download

        with open("download_times.csv", "a") as f:
            f.write(f"{ehr_key},{label},{download_latency:.3f}\n")

        print(f"📥 Download latency ({label}): {download_latency:.3f} seconds")
    except Exception as e:
        print(f"⚠️ Failed to download {label} with CID {cid}: {e}")
