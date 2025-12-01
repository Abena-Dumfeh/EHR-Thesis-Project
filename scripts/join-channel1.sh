#!/bin/bash
# stop any error
set -e

# This script creates ehrchannel1, joins Hospital1 peers to it, and updates anchor peers

# ------------------------------------------
# SETUP VARIABLES
# ------------------------------------------
CHANNEL_NAME="ehrchannel1"
ORDERER_ADDRESS="orderer1.example.com:7050"

CHANNEL_TX_PATH="/opt/gopath/src/github.com/hyperledger/fabric/peer/channel-artifacts/${CHANNEL_NAME}.tx"
CHANNEL_BLOCK_PATH="/opt/gopath/src/github.com/hyperledger/fabric/peer/channel-artifacts/${CHANNEL_NAME}.block"
TLS_CA_CERT="/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer1.example.com/msp/tlscacerts/tlsca.example.com-cert.pem"

# ------------------------------------------
# CHECK IF TX FILE EXISTS INSIDE CONTAINER
# ------------------------------------------
if ! docker exec cli.adminorg.hospital1 test -f "$CHANNEL_TX_PATH"; then
  echo "❌ ERROR: Channel transaction file not found at $CHANNEL_TX_PATH (inside container)"
  exit 1
fi

# ------------------------------------------
# FUNCTION TO VERIFY ENV VARS IN CLI
# ------------------------------------------
verify_env() {
  CLI=$1
  echo -e "\n🔍 Verifying environment variables in $CLI..."
  docker exec $CLI printenv | grep CORE_PEER
}

# ------------------------------------------
# CREATE CHANNEL
# ------------------------------------------
echo "Creating channel ${CHANNEL_NAME}..."

docker exec -e CORE_PEER_LOCALMSPID="AdminOrgHospital1MSP" \
  -e CORE_PEER_MSPCONFIGPATH="/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/adminorg.hospital1.com/users/Admin@adminorg.hospital1.com/msp" \
  -e CORE_PEER_ADDRESS="peer0.adminorg.hospital1.com:7051" \
  -e CORE_PEER_TLS_ENABLED=true \
  -e CORE_PEER_TLS_ROOTCERT_FILE="/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/adminorg.hospital1.com/peers/peer0.adminorg.hospital1.com/tls/ca.crt" \
  cli.adminorg.hospital1 \
  peer channel create -o "$ORDERER_ADDRESS" -c "$CHANNEL_NAME" \
  -f "$CHANNEL_TX_PATH" \
  --outputBlock "$CHANNEL_BLOCK_PATH" \
  --tls --cafile "$TLS_CA_CERT"

verify_env cli.adminorg.hospital1

# ------------------------------------------
# CHECK IF BLOCK FILE EXISTS INSIDE CONTAINER
# ------------------------------------------
if ! docker exec cli.adminorg.hospital1 test -f "$CHANNEL_BLOCK_PATH"; then
  echo "❌ ERROR: Channel block not found at $CHANNEL_BLOCK_PATH (inside container)"
  exit 1
fi

# ------------------------------------------
# FUNCTION TO JOIN PEER TO CHANNEL
# ------------------------------------------
join_peer() {
  ORG_NAME=$1
  CLI_CONTAINER=$2
  MSP_ID=$3
  MSP_PATH=$4
  PEER_ADDRESS=$5
  TLS_ROOTCERT=$6

  echo "Joining $ORG_NAME to channel $CHANNEL_NAME..."
  docker exec -e CORE_PEER_LOCALMSPID="$MSP_ID" \
    -e CORE_PEER_MSPCONFIGPATH="$MSP_PATH" \
    -e CORE_PEER_ADDRESS="$PEER_ADDRESS" \
    -e CORE_PEER_TLS_ENABLED=true \
    -e CORE_PEER_TLS_ROOTCERT_FILE="$TLS_ROOTCERT" \
    "$CLI_CONTAINER" \
    peer channel join -b "$CHANNEL_BLOCK_PATH" \
    --orderer "$ORDERER_ADDRESS" --tls --cafile "$TLS_CA_CERT"

  verify_env "$CLI_CONTAINER"
}

# ------------------------------------------
# FUNCTION TO UPDATE ANCHOR PEER
# ------------------------------------------
update_anchor_peer() {
  ORG_NAME=$1
  CLI_CONTAINER=$2
  MSP_ID=$3
  MSP_PATH=$4
  PEER_ADDRESS=$5
  TLS_ROOTCERT=$6
  TX_FILE=$7

  echo "Updating anchor peer for $ORG_NAME..."
  docker exec -e CORE_PEER_LOCALMSPID="$MSP_ID" \
    -e CORE_PEER_MSPCONFIGPATH="$MSP_PATH" \
    -e CORE_PEER_ADDRESS="$PEER_ADDRESS" \
    -e CORE_PEER_TLS_ENABLED=true \
    -e CORE_PEER_TLS_ROOTCERT_FILE="$TLS_ROOTCERT" \
    "$CLI_CONTAINER" \
    peer channel update -o "$ORDERER_ADDRESS" -c "$CHANNEL_NAME" \
    -f "/opt/gopath/src/github.com/hyperledger/fabric/peer/channel-artifacts/${TX_FILE}" \
    --tls --cafile "$TLS_CA_CERT"

  verify_env "$CLI_CONTAINER"
}

# ------------------------------------------
# Join and Update Anchor Peers for Hospital1
# ------------------------------------------
join_peer "AdminOrgHospital1" "cli.adminorg.hospital1" \
  "AdminOrgHospital1MSP" \
  "/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/adminorg.hospital1.com/users/Admin@adminorg.hospital1.com/msp" \
  "peer0.adminorg.hospital1.com:7051" \
  "/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/adminorg.hospital1.com/peers/peer0.adminorg.hospital1.com/tls/ca.crt"

update_anchor_peer "AdminOrgHospital1" "cli.adminorg.hospital1" \
  "AdminOrgHospital1MSP" \
  "/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/adminorg.hospital1.com/users/Admin@adminorg.hospital1.com/msp" \
  "peer0.adminorg.hospital1.com:7051" \
  "/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/adminorg.hospital1.com/peers/peer0.adminorg.hospital1.com/tls/ca.crt" \
  "AdminOrgHospital1MSPanchors_ehrchannel1.tx"

join_peer "PatientOrgHospital1" "cli.patientorg.hospital1" \
  "PatientOrgHospital1MSP" \
  "/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/patientorg.hospital1.com/users/Admin@patientorg.hospital1.com/msp" \
  "peer0.patientorg.hospital1.com:9051" \
  "/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/patientorg.hospital1.com/peers/peer0.patientorg.hospital1.com/tls/ca.crt"

update_anchor_peer "PatientOrgHospital1" "cli.patientorg.hospital1" \
  "PatientOrgHospital1MSP" \
  "/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/patientorg.hospital1.com/users/Admin@patientorg.hospital1.com/msp" \
  "peer0.patientorg.hospital1.com:9051" \
  "/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/patientorg.hospital1.com/peers/peer0.patientorg.hospital1.com/tls/ca.crt" \
  "PatientOrgHospital1MSPanchors_ehrchannel1.tx"

join_peer "DoctorOrgHospital1" "cli.doctororg.hospital1" \
  "DoctorOrgHospital1MSP" \
  "/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/doctororg.hospital1.com/users/Admin@doctororg.hospital1.com/msp" \
  "peer0.doctororg.hospital1.com:10051" \
  "/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/doctororg.hospital1.com/peers/peer0.doctororg.hospital1.com/tls/ca.crt"

join_peer "DoctorOrgHospital1" "cli.peer1.doctororg.hospital1" \
  "DoctorOrgHospital1MSP" \
  "/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/doctororg.hospital1.com/users/Admin@doctororg.hospital1.com/msp" \
  "peer1.doctororg.hospital1.com:11051" \
  "/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/doctororg.hospital1.com/peers/peer1.doctororg.hospital1.com/tls/ca.crt"

update_anchor_peer "DoctorOrgHospital1" "cli.doctororg.hospital1" \
  "DoctorOrgHospital1MSP" \
  "/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/doctororg.hospital1.com/users/Admin@doctororg.hospital1.com/msp" \
  "peer0.doctororg.hospital1.com:10051" \
  "/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/doctororg.hospital1.com/peers/peer0.doctororg.hospital1.com/tls/ca.crt" \
  "DoctorOrgHospital1MSPanchors_ehrchannel1.tx"

echo -e "\n✅ '$CHANNEL_NAME' setup complete: all Hospital1 peers joined and anchor peers updated."
