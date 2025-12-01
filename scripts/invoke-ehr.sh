#!/bin/bash
set -e

CHANNEL_NAME="ehrchannel2"
CHAINCODE_NAME="ehr"
ORDERER_ADDRESS="orderer1.example.com:7050"
ORDERER_TLS_CA="/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer1.example.com/msp/tlscacerts/tlsca.example.com-cert.pem"

# Parameters for the record to be created
PATIENT_ID="patient123"
NAME="John Doe"
DIAGNOSIS="Flu"
TREATMENT="Rest and hydration"

# AdminOrgHospital1 will invoke the chaincode
docker exec \
  -e CORE_PEER_LOCALMSPID="AdminOrgHospital1MSP" \
  -e CORE_PEER_MSPCONFIGPATH="/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/adminorg.hospital1.com/users/Admin@adminorg.hospital1.com/msp" \
  -e CORE_PEER_ADDRESS="peer0.adminorg.hospital1.com:7051" \
  -e CORE_PEER_TLS_ENABLED=true \
  -e CORE_PEER_TLS_ROOTCERT_FILE="/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/adminorg.hospital1.com/peers/peer0.adminorg.hospital1.com/tls/ca.crt" \
  cli.adminorg.hospital1 \
  peer chaincode invoke \
    -o "$ORDERER_ADDRESS" \
    --ordererTLSHostnameOverride orderer1.example.com \
    --tls \
    --cafile "$ORDERER_TLS_CA" \
    -C "$CHANNEL_NAME" \
    -n "$CHAINCODE_NAME" \
    --peerAddresses peer0.adminorg.hospital1.com:7051 \
    --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/adminorg.hospital1.com/peers/peer0.adminorg.hospital1.com/tls/ca.crt \
    --peerAddresses peer0.patientorg.hospital1.com:9051 \
    --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/patientorg.hospital1.com/peers/peer0.patientorg.hospital1.com/tls/ca.crt \
    --peerAddresses peer0.doctororg.hospital1.com:10051 \
    --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/doctororg.hospital1.com/peers/peer0.doctororg.hospital1.com/tls/ca.crt \
    --peerAddresses peer0.adminorg.hospital2.com:11051 \
    --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/adminorg.hospital2.com/peers/peer0.adminorg.hospital2.com/tls/ca.crt \
    --peerAddresses peer0.doctororg.hospital2.com:12051 \
    --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/doctororg.hospital2.com/peers/peer0.doctororg.hospital2.com/tls/ca.crt \
    -c '{"function":"CreateRecord","Args":["'"$PATIENT_ID"'","'"$NAME"'","'"$DIAGNOSIS"'","'"$TREATMENT"'"]}'

echo "✅ Invoke transaction submitted: Created record for patient ID '$PATIENT_ID'"
