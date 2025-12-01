import time
import subprocess
from encrypt_file_aes import encrypt_file
from upload_ckks_encrypted import encrypt_ckks, extract_numbers_from_fhir, upload_to_ipfs

# === Config ===
FHIR_PATH = '../files/sample_fhir_ehr.json'
AES_OUT_PATH = FHIR_PATH + '.enc'
CKKS_BIN_PATH = '../files/encrypted_values.ckks.bin'
CONTEXT_PATH = '../files/context.ckks.tenseal'
EHR_ID = 'ehr_latency_001'

start = time.time()

# Step 1: AES encryption
aes_path = encrypt_file(FHIR_PATH)

# Step 2: CKKS encryption
numbers = extract_numbers_from_fhir(FHIR_PATH)
encrypt_ckks(numbers, CKKS_BIN_PATH, CONTEXT_PATH)

# Step 3: Upload to IPFS
aes_cid = upload_to_ipfs(aes_path)
ckks_cid = upload_to_ipfs(CKKS_BIN_PATH)
fhir_cid = upload_to_ipfs(FHIR_PATH)
fhir_enc_cid = upload_to_ipfs(aes_path)

# Step 4: Blockchain transaction (update these values as needed)
invoke_cmd = [
    'docker', 'exec', 'cli.doctororg.hospital1', 'peer', 'chaincode', 'invoke',
    '-o', 'orderer1.example.com:7050',
    '--ordererTLSHostnameOverride', 'orderer1.example.com',
    '--tls',
    '--cafile', '/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer1.example.com/msp/tlscacerts/tlsca.example.com-cert.pem',
    '-C', 'ehrchannel1',
    '-n', 'ehr',
    '-c', f'{{"Args":["CreateEHRRecord","{EHR_ID}","patient01","Vitals","QmRKnmWfEyrY2oqZC5m4m5w5SA1o358vr7DUcBkLZnPR3B","QmZxHCd7Y88Ms9bRew16exkJMmMYvE4iea9EnQx89nFX47","QmVatRVkJfcWaJ3QXiEbaPqzcDT6x96afKQWGQVXhVDGTa","QmRKnmWfEyrY2oqZC5m4m5w5SA1o358vr7DUcBkLZnPR3B","true"]}}',
    '--peerAddresses', 'peer0.doctororg.hospital1.com:10051',
    '--tlsRootCertFiles', '/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/doctororg.hospital1.com/peers/peer0.doctororg.hospital1.com/tls/ca.crt'
]

subprocess.run(invoke_cmd, check=True)

end = time.time()
latency = end - start
print(f"⏱️ Total EHR Upload Latency: {latency:.2f} seconds")
