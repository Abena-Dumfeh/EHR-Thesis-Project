🏥 Patient-Centric Healthcare Data Management System (PCHDM)

Abstract
This project presents a privacy-preserving, patient-centric healthcare data management system 
that leverages blockchain and decentralized storage technologies to ensure secure, transparent, 
and controlled access to Electronic Health Records (EHRs).
The system integrates Hyperledger Fabric, IPFS, and advanced encryption techniques (AES & CKKS) 
to address key challenges in healthcare data sharing, including data privacy, ownership, and interoperability.


Key Contributions
Designed an organization Hyperledger Fabric network with secure channel communication.
Implemented patient-controlled consent management using smart contracts.
Integrated IPFS for off-chain storage with blockchain-based hash verification
Applied AES encryption for storage and CKKS homomorphic encryption for secure computation
Developed a CLI-based full-stack system prototype supporting Admin, Doctor, and Patient roles
Ensured FHIR-compliant healthcare data formatting

🏗️ System Architecture
📊 Architecture Diagram




🔍 Description

The system consists of:

Blockchain Layer (Hyperledger Fabric)
Handles identity, access control, and immutable logging
Off-chain Storage (IPFS)
Stores encrypted EHR files
Application Layer (Flask Backend)
Handles business logic, encryption, and API routing
Database (MySQL)
Stores metadata (CID, user info, access logs)
🚀 Features
🔐 End-to-end encrypted EHR storage
👤 Patient-controlled data access (grant/revoke)
⛓️ Immutable audit logs via blockchain
📁 Decentralized file storage (IPFS)
🧠 Privacy-preserving computation (CKKS)
🏥 Multi-hospital interoperability via channels
🛠️ Tech Stack
Layer	Technology
Blockchain	Hyperledger Fabric
Storage	IPFS
Backend	Python (Flask)
Smart Contracts	Go (Chaincode)
Database	MySQL
Encryption	AES, CKKS (TenSEAL)
DevOps	Docker, Docker Compose


⚙️ Setup Instructions
1️⃣ Clone Repository
git clone https://github.com/yourusername/pchdm.git
cd pchdm

2️⃣ Generate Crypto & Artifacts
./scripts/gen-crypto.sh
./scripts/gen-genesis.sh
./scripts/gen-channels.sh

3️⃣ Start Network
docker-compose up -d

4️⃣ Create Channel & Join Peers
./scripts/join-channel1.sh

5️⃣ Run Backend
cd backend
pip install -r requirements.txt
python app.py

▶️ Usage Workflow
Doctor uploads EHR → encrypted + stored on IPFS
CID stored in MySQL + blockchain
Patient grants/revokes access via smart contract
Authorized users retrieve and decrypt data

📸 Screenshots
🔐 Login System




🏥 Doctor Upload Interface




👤 Patient Dashboard




📊 Performance Evaluation
Chaincode execution latency measured
Block creation time analyzed
EHR upload & retrieval latency evaluated
Encryption overhead assessed


🔐 Security Analysis
AES encryption ensures data confidentiality
CKKS enables computation on encrypted data
Blockchain guarantees immutability and auditability
Role-based access enforced via smart contracts

📂 Project Structure
ehr/
├── chaincode/
├── backend/
├── scripts/
├── docker-compose/
├── channel-artifacts/
├── crypto-material/
├── docs/
│   ├── architecture.png
│   └── screenshots/

👤 Author

Maame Abena Dumfeh
MSc Computer Engineering
Focus: Blockchain, Cybersecurity & Privacy-Preserving Systems

📌 Future Work
Full homomorphic encryption integration for all operations
AI-based disease prediction on encrypted data
Deployment on cloud infrastructure
