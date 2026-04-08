🏥 PATIENT-CENTRIC HEALTHCARE DATA MANAGEMENT SYSTEM (PCHDM)

ABSTRACT

This project presents a privacy-preserving, patient-centric healthcare data management system 
that leverages blockchain and decentralized storage technologies to ensure secure, transparent, 
and controlled access to Electronic Health Records (EHRs).
The system integrates Hyperledger Fabric, IPFS, and advanced encryption techniques (AES & CKKS) 
to address key challenges in healthcare data sharing, including data privacy, ownership, and interoperability.


KEY CONTRIBUTIONS

Designed an organization Hyperledger Fabric network with secure channel communication.

Implemented patient-controlled consent management using smart contracts.

Integrated IPFS for off-chain storage with blockchain-based hash verification

Applied AES encryption for storage and CKKS homomorphic encryption for secure computation

Developed a CLI-based full-stack system prototype supporting Admin, Doctor, and Patient roles

Ensured FHIR-compliant healthcare data formatting


🏗️ System Architecture

📊 Architecture Diagram: <img width="686" height="355" alt="Screenshot from 2026-04-08 18-41-18" src="https://github.com/user-attachments/assets/9a2bbdfd-2f63-4b62-b389-d725ab010638" />

1. Fabric Network Diagram: <img width="519" height="376" alt="Screenshot from 2026-04-08 18-31-12" src="https://github.com/user-attachments/assets/ed775eb6-ea35-4ffa-b698-b27687e39d6e" />

2. Workflow for encrypted EHR upload to IPFS: <img width="570" height="291" alt="Screenshot from 2026-04-08 18-36-35" src="https://github.com/user-attachments/assets/c94a6d30-b5e8-4457-a4a8-be78927d4f55" />

3. Role-Based Acces Control Model: <img width="634" height="276" alt="Screenshot from 2026-04-08 18-43-53" src="https://github.com/user-attachments/assets/bdb03d9f-8e21-4902-905e-fc2649fbcfc9" />


🛠️ TECH STACK

Blockchain: 	Hyperledger Fabric

Storage:	IPFS

Backend:	Python (Flask)

Smart Contracts:	Go (Chaincode)

Database:	MySQL

Encryption:	AES, CKKS (TenSEAL)

DevOps:	Docker, Docker Compose


⚙️ SETUP INSTRUCTIONS

1️⃣ Clone Repository: 

git clone https://github.com/Abena-Dumfeh/EHR-Thesis-Project.git 

cd EHR-Thesis-Project


2️⃣ Generate Crypto & Artifacts: 

./scripts/gen-crypto.sh 

./scripts/gen-genesis.sh 

./scripts/gen-channels.sh

3️⃣ Start Network: 

docker-compose up -d

4️⃣ Create Channel & Join Peers: 

./scripts/join-channel1.sh

5️⃣ Run Backend: 

cd backend 

pip install -r requirements.txt 

python app.py


▶️ USAGE WORKFLOW: 

Doctor uploads EHR → encrypted + stored on IPFS

CID stored in MySQL + blockchain

Patient grants/revokes access via smart contract

Authorized users retrieve and decrypt data


RESULTS

📊 Performance Evaluation

1. Chaincode execution latency measured: Most functions executed within 0.172s to 0.190s, indicating excellent query/invoke performance.

2. Block creation time analyzed: Block Creation Time ≈ 57 seconds

3. EHR upload latency: Although the file sizes differed significantly (1.35 KiB for AES and 835.27 KiB for CKKS), both were uploaded to IPFS in under 0.15 seconds.

4. EHR retrieval latency: The AES-encrypted file (1.38 KB) was downloaded in 0.058 seconds, while the much larger CKKS-encrypted file (835.27 KB) was retrieved in 0.065 seconds. These results indicate that download latency is minimal and relatively unaffected by file size, especially in a local IPFS environment.

5. Encryption overhead assessed: The encryption overhead is evident as the original EHR document (1.4 KB) and its extracted plaintext values (129 bytes) increase significantly to 836 KB after CKKS encryption.


🔐 Security Analysis

AES encryption ensures data confidentiality

CKKS enables computation on encrypted data

Blockchain guarantees immutability and auditability

Role-based access enforced via smart contracts



📂 Project Structure

ehr/

├── chaincode/

├── config/

├── docker/

├── encryption/

├── ipfs-storage/

├── scripts/

├── sql/

├── temp_ehr


📌 Future Work: 

Full homomorphic encryption integration for all operations |
AI-based disease prediction on encrypted data | 
Deployment on cloud infrastructure
