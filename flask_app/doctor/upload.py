import os
#from flask import Blueprint, request, render_template
#import ipfshttpclient
import tenseal as ts
#from scripts.fhir_converter import create_fhir_observation
import re
import json
from datetime import datetime
import pdfplumber
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

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

    data = {
        "resourceType": "DocumentReference",
        "status": "current",
        "type": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "34108-1",
                    "display": record_type
                }
            ],
            "text": record_type
        },
        "subject": {"reference": f"{receiver_type}/{receiver_id or 'unknown'}"},
        "description": notes or "",
        "date": datetime.utcnow().isoformat() + "Z",
        "author": [{"reference": f"Practitioner/{receiver_id or 'unknown'}"}],
        "custodian": {"reference": "Organization/Hospital1"},
        "content": [
            {
                "attachment": {
                    "contentType": "text/plain",
                    "data": text
                }
            }
        ]
    }

    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)

    return json_path

def generate_vitals_fhir_json(ehr_key, patient_id, bp, glucose, cholesterol, notes):
    json_path = f"./files/{ehr_key}_vitals_fhir.json"

    fhir_data = {
        "resourceType": "DocumentReference",
        "status": "current",
        "type": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "8716-3",
                    "display": "Vital signs"
                }
            ],
            "text": "Vital Signs Record"
        },
        "subject": {"reference": f"patient/{patient_id}"},
        "description": notes or "Vital signs record",
        "date": datetime.utcnow().isoformat() + "Z",
        "author": [{"reference": f"Practitioner/{patient_id}"}],
        "custodian": {"reference": "Organization/Hospital1"},
        "content": [
            {
                "attachment": {
                    "contentType": "application/json",
                    "data": json.dumps({
                        "blood_pressure": bp,
                        "glucose_level": glucose,
                        "cholesterol": cholesterol
                    })
                }
            }
        ]
    }

    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, 'w') as f:
        json.dump(fhir_data, f, indent=2)

    return json_path

def validate_fhir_json(data):
    required_fields = ['resourceType', 'subject', 'type', 'content']
    return all(field in data for field in required_fields)

def extract_numbers_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    numbers = [float(n) for n in re.findall(r'\b\d+(?:\.\d+)?\b', content)]
    return numbers


def encrypt_file_aes(input_path):
    with open(input_path, 'rb') as f:
        data = f.read()
    key = get_random_bytes(32)
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    output_path = input_path + '.aes'
    with open(output_path, 'wb') as f:
        f.write(cipher.nonce + tag + ciphertext)
    return output_path, key


def encrypt_ckks_vector(values):
    context = ts.context(
        ts.SCHEME_TYPE.CKKS,
        poly_modulus_degree=8192,
        coeff_mod_bit_sizes=[60, 40, 40, 60]
    )
    context.global_scale = 2**40
    context.generate_galois_keys()
    vector = ts.ckks_vector(context, values)
    return vector.serialize(), context.serialize(save_secret_key=True)


def save_ckks_context(context_bytes, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'wb') as f:
        f.write(context_bytes)
