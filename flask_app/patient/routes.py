from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
import mysql.connector
import os
import json
from datetime import datetime
from Crypto.Cipher import AES
#from utils.security import encrypt_field, check_password, hash_password

#from utils.security import encrypt_field, check_password, hash_password

#from utils.security import decrypt_field

from dotenv import load_dotenv
load_dotenv()
AES_KEY = os.getenv("AES_SECRET_KEY").encode()

patient_bp = Blueprint('patient_bp', __name__, template_folder='templates/patient')
bcrypt = Bcrypt()  # This will be initialized from app context

def decrypt_aes_file(file_path):
    with open(file_path, 'rb') as f:
        encrypted_data = f.read()

    key = AES_KEY  # ✅ now loaded from .env
    nonce = encrypted_data[:16]
    tag = encrypted_data[16:32]
    ciphertext = encrypted_data[32:]

    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    decrypted = cipher.decrypt_and_verify(ciphertext, tag)
    return decrypted.decode('utf-8')

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='ehruser',
        password='StrongPass2025!',
        database='ehrdb'
    )

@patient_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        contact = request.form['contact']
        dob = request.form['dob']
        address = request.form['address']
        password = request.form['password']

        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM patients WHERE email = %s", (email,))
        existing = cursor.fetchone()
        if existing:
            flash('Email already registered.', 'error')
            conn.close()
            return render_template('register.html')

        cursor.execute("""
            INSERT INTO patients (name, email, contact, dob, address, password_hash)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, email, contact, dob, address, password_hash))

        conn.commit()
        cursor.close()
        conn.close()

        flash('Registration successful. Please log in.')
        return redirect(url_for('patient_bp.login'))

    return render_template('patient/register.html')

@patient_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM patients WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and bcrypt.check_password_hash(user['password_hash'], password):
            session['patient_id'] = user['patient_id']
            session['patient_name'] = user['name']
            flash('Login successful!', 'success')
            return redirect(url_for('patient_bp.dashboard'))
        else:
            flash('Invalid email or password', 'error')

    return render_template('patient/login.html')


@patient_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('patient_bp.login'))

@patient_bp.route('/dashboard')
def dashboard():
    if 'patient_id' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('patient_bp.login'))

    patient_id = session['patient_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch EHR metadata
    cursor.execute("""
        SELECT ehr_id, record_type, ipfs_cid, encryption_type, created_at
        FROM ehr_records
        WHERE patient_id = %s
        ORDER BY created_at DESC
    """, (patient_id,))
    records = cursor.fetchall()
    cursor.close()
    conn.close()

    # Decrypt and load content
    for record in records:
        cid = record['ipfs_cid']
        local_path = f'temp_ehr/{cid}.aes'
        os.makedirs('temp_ehr', exist_ok=True)

        # Download from IPFS (once per record)
        if not os.path.exists(local_path):
            os.system(f'ipfs get {cid} -o {local_path}')

        try:
            decrypted_json = decrypt_aes_file(local_path)
            record['decrypted'] = json.loads(decrypted_json)
        except Exception as e:
            record['decrypted'] = {"error": f"Decryption failed: {str(e)}"}

    return render_template('patient/dashboard.html', records=records, name=session['patient_name'])


@patient_bp.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'patient_id' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('patient_bp.login'))

    patient_id = session['patient_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        contact = request.form['contact']
        address = request.form['address']

        cursor.execute("""
            UPDATE patients SET contact = %s, address = %s
            WHERE patient_id = %s
        """, (contact, address, patient_id))

        conn.commit()
        cursor.close()
        conn.close()

        flash('Profile updated successfully.', 'success')
        return redirect(url_for('patient_bp.dashboard'))

    # Pre-fill current info
    cursor.execute("SELECT contact, address FROM patients WHERE patient_id = %s", (patient_id,))
    patient = cursor.fetchone()

    cursor.close()
    conn.close()
    return render_template('patient/edit_profile.html', patient=patient)

@patient_bp.route('/consent', methods=['GET'])
def consent_management():
    if 'patient_id' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('patient_bp.login'))

    patient_id = session['patient_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get EHR records owned by this patient
    cursor.execute("""
        SELECT ehr_id, record_type, created_at FROM ehr_records
        WHERE patient_id = %s
    """, (patient_id,))
    ehr_list = cursor.fetchall()

    # Get all doctors
    cursor.execute("SELECT doctor_id, name FROM doctors")
    doctors = cursor.fetchall()

    # Get current consents
    cursor.execute("""
        SELECT cl.consent_id, cl.ehr_id, d.name AS doctor_name, cl.granted, cl.granted_at, cl.revoked_at
        FROM consent_logs cl
        JOIN doctors d ON cl.doctor_id = d.doctor_id
        WHERE cl.patient_id = %s
        ORDER BY cl.granted_at DESC
    """, (patient_id,))
    consents = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('patient/consent.html', ehr_list=ehr_list, doctors=doctors, consents=consents)

@patient_bp.route('/grant_consent', methods=['POST'])
def grant_consent():
    if 'patient_id' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('patient_bp.login'))

    ehr_id = request.form['ehr_id']
    doctor_id = request.form['doctor_id']
    patient_id = session['patient_id']

    now = datetime.utcnow()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert consent log
    cursor.execute("""
        INSERT INTO consent_logs (ehr_id, patient_id, doctor_id, granted, granted_at)
        VALUES (%s, %s, %s, %s, %s)
    """, (ehr_id, patient_id, doctor_id, True, now))

    conn.commit()
    cursor.close()
    conn.close()
    flash('Consent granted.', 'success')
    return redirect(url_for('patient_bp.consent_management'))

@patient_bp.route('/revoke_consent/<int:consent_id>', methods=['POST'])
def revoke_consent(consent_id):
    if 'patient_id' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('patient_bp.login'))

    now = datetime.utcnow()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE consent_logs SET granted = %s, revoked_at = %s
        WHERE consent_id = %s
    """, (False, now, consent_id))

    conn.commit()
    cursor.close()
    conn.close()
    flash('Consent revoked.', 'info')
    return redirect(url_for('patient_bp.consent_management'))

@patient_bp.route('/download/<cid>')
def download_ehr(cid):
    from flask import send_file
    local_path = f'temp_ehr/{cid}.aes'
    decrypted_path = f'temp_ehr/{cid}_decrypted.json'

    try:
        if not os.path.exists(local_path):
            os.system(f'ipfs get {cid} -o {local_path}')

        decrypted_json = decrypt_aes_file(local_path)
        with open(decrypted_path, 'w') as f:
            f.write(decrypted_json)

        return send_file(decrypted_path, as_attachment=True)

    except Exception as e:
        flash(f"Download failed: {e}", 'error')
        return redirect(url_for('patient_bp.dashboard'))
