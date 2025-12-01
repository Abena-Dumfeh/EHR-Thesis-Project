import mysql.connector
import bcrypt
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
import base64

# ===================== AES ENCRYPTION =====================
AES_KEY = b'ThisIsASecretKey1234567890123456'  # 32 bytes for AES-256

def encrypt_field(plaintext):
    iv = get_random_bytes(16)
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    padded = pad(plaintext.encode(), AES.block_size)
    encrypted = cipher.encrypt(padded)
    return base64.b64encode(iv + encrypted).decode()

# ===================== BCRYPT HASHING =====================
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# ===================== DATABASE INSERT =====================
def insert_user_to_db(user_id, role, msp_id, name, email, contact, address, dob, password):
    try:
        # Encrypt fields
        enc_name = encrypt_field(name)
        enc_email = encrypt_field(email)
        enc_contact = encrypt_field(contact)
        enc_address = encrypt_field(address)
        enc_dob = encrypt_field(dob)
        hashed_pw = hash_password(password)

        # Connect to MySQL
        conn = mysql.connector.connect(
            host="localhost",
            user="ehruser",
            password="StrongPass2025!",
            database="ehrdb"
        )
        cursor = conn.cursor()

        query = """
        INSERT INTO users (
            user_id, role, msp_id, encrypted_name, encrypted_email,
            encrypted_contact, encrypted_address, encrypted_dob,
            password_hash, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'active')
        """

        cursor.execute(query, (
            user_id, role, msp_id, enc_name, enc_email,
            enc_contact, enc_address, enc_dob, hashed_pw
        ))

        conn.commit()
        cursor.close()
        conn.close()

        print(f"✅ {role.capitalize()} '{user_id}' inserted successfully.")

    except Exception as e:
        print("❌ Error inserting user:", e)

# ===================== MAIN (CLI Input for Now) =====================
if __name__ == "__main__":
    print("🔐 Add New Encrypted User")
    user_id = input("User ID: ")
    role = input("Role (admin/doctor/patient): ").strip().lower()
#    msp_id = input("MSP ID (e.g., AdminOrgMSP): ")
    role = input("Role (admin/doctor/patient): ").strip().lower()

# Auto-assign msp_id based on role
    if role == "admin":
        msp_id = "AdminOrgMSP"
    elif role == "doctor":
        msp_id = "DoctorOrgHospital1MSP"
    elif role == "patient":
        msp_id = "PatientOrgHospital1MSP"
    else:
        print("❌ Invalid role. Must be admin, doctor, or patient.")
        exit()

    name = input("Name: ")
    email = input("Email: ")
    contact = input("Contact Number: ")
    address = input("Address: ")
    dob = input("Date of Birth (YYYY-MM-DD): ")
    password = input("Password: ")

    insert_user_to_db(user_id, role, msp_id, name, email, contact, address, dob, password)
