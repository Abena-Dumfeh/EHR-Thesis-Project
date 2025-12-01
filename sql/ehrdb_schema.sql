-- Drop tables in reverse dependency order (avoid foreign key errors)
DROP TABLE IF EXISTS access_logs;
DROP TABLE IF EXISTS ipfs_records;
DROP TABLE IF EXISTS users;

-- USERS Table: stores encrypted user profiles and Fabric identity links
CREATE TABLE users (
    user_id CHAR(64) PRIMARY KEY,  -- UUID or Fabric identity
    role ENUM('admin', 'doctor', 'patient') NOT NULL,
    msp_id VARCHAR(128) NOT NULL,  -- e.g., DoctorOrgMSP
    encrypted_name TEXT NOT NULL,
    encrypted_email TEXT,
    encrypted_contact TEXT,
    encrypted_address TEXT,
    encrypted_dob TEXT,
    password_hash TEXT NOT NULL,   -- bcrypt
    status ENUM('active', 'inactive', 'banned') DEFAULT 'active',
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- IPFS_RECORDS Table: stores EHR metadata and IPFS CIDs
CREATE TABLE ipfs_records (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    ehr_id VARCHAR(64) UNIQUE NOT NULL,             -- EHR record ID (CID reference)
    patient_id CHAR(64) NOT NULL,                   -- FK to users.user_id
    ipfs_cid TEXT NOT NULL,                         -- IPFS CID of encrypted file
    file_type VARCHAR(64),                          -- e.g., Diagnosis, LabResult
    encryption_type ENUM('AES', 'CKKS', 'BFV') NOT NULL,
    uploaded_by_user_id CHAR(64),                   -- FK to users.user_id
    notes TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign keys
    FOREIGN KEY (patient_id) REFERENCES users(user_id),
    FOREIGN KEY (uploaded_by_user_id) REFERENCES users(user_id)
);

-- ACCESS_LOGS Table: tracks who accessed what and why
CREATE TABLE access_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id CHAR(64) NOT NULL,                   -- FK to users.user_id
    accessor_user_id CHAR(64) NOT NULL,             -- FK to users.user_id
    accessor_role ENUM('doctor', 'admin') NOT NULL,
    action ENUM('VIEW', 'DOWNLOAD', 'MODIFY') NOT NULL,
    ehr_id VARCHAR(64) DEFAULT NULL,                -- FK to ipfs_records.ehr_id
    reason TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign keys
    FOREIGN KEY (patient_id) REFERENCES users(user_id),
    FOREIGN KEY (accessor_user_id) REFERENCES users(user_id),
    FOREIGN KEY (ehr_id) REFERENCES ipfs_records(ehr_id)
);
