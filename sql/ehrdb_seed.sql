-- Insert encrypted patient
INSERT INTO users (
    user_id,
    role,
    msp_id,
    encrypted_name,
    encrypted_email,
    encrypted_contact,
    encrypted_address,
    encrypted_dob,
    password_hash,
    status
) VALUES (
    'patient123',
    'patient',
    'PatientOrgHospital1MSP',
    'ENC(name:Abena Kofi)',
    'ENC(email:abena@ehr.com)',
    'ENC(contact:010-1234-5678)',
    'ENC(address:Busan)',
    'ENC(dob:1995-06-20)',
    '$2b$12$FakeHashedPasswordForPatient', -- bcrypt placeholder
    'active'
);

-- Insert encrypted doctor
INSERT INTO users (
    user_id,
    role,
    msp_id,
    encrypted_name,
    encrypted_email,
    encrypted_contact,
    encrypted_address,
    encrypted_dob,
    password_hash,
    status
) VALUES (
    'doctor456',
    'doctor',
    'DoctorOrgHospital1MSP',
    'ENC(name:Dr. Mensah)',
    'ENC(email:mensah@hospital.com)',
    'ENC(contact:010-5678-1234)',
    'ENC(address:Seoul)',
    'ENC(dob:1980-12-01)',
    '$2b$12$FakeHashedPasswordForDoctor', -- bcrypt placeholder
    'active'
);

-- Insert EHR record for patient, uploaded by doctor
INSERT INTO ipfs_records (
    ehr_id,
    patient_id,
    ipfs_cid,
    file_type,
    encryption_type,
    uploaded_by_user_id,
    notes
) VALUES (
    'ehr001',
    'patient123',
    'QmTestCID123FakeForDemo',
    'Diagnosis',
    'CKKS',
    'doctor456',
    'Encrypted diagnosis report stored in IPFS'
);

-- Doctor views EHR
INSERT INTO access_logs (
    patient_id,
    accessor_user_id,
    accessor_role,
    action,
    ehr_id,
    reason
) VALUES (
    'patient123',
    'doctor456',
    'doctor',
    'VIEW',
    'ehr001',
    'Reviewed patient report before prescription'
);
