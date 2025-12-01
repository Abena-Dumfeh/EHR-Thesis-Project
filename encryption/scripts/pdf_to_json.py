from PyPDF2 import PdfReader
import json
import re

pdf_path = '../input/ehr_patient_record.pdf'
json_path = '../output/ehr_values.json'

reader = PdfReader(pdf_path)
text = "".join([page.extract_text() for page in reader.pages])

numbers = [float(n) for n in re.findall(r'\b\d+(?:\.\d+)?\b', text)]

with open(json_path, 'w') as f:
    json.dump({"numeric_values": numbers}, f, indent=2)

print(f"✅ Extracted values saved: {json_path}")
