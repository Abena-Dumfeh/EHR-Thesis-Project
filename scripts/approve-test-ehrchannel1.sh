#!/bin/bash

set -e

CHANNEL_NAME="ehrchannel1"
CHAINCODE_NAME="test"
CHAINCODE_VERSION="1"
CHAINCODE_SEQUENCE="1"
CHAINCODE_LABEL="test_1"
PACKAGE_ID="test_1:90a1130de3adf6fd899c88af967ad24a295e4e7e35b20dd79dc56dc65f249da3"
INIT_REQUIRED="--init-required"

ORDERER_TLS_CA="/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer1.example.com/msp/tlscacerts/tlsca.example.com-cert.pem"
ORDERER_ADDRESS="orderer1.example.com:7050"
ORDERER_TLS_OVERRIDE="orderer1.example.com"

# Declare the list of CLI containers and their environment variables
declare -A CLI_ENV=(
  ["cli.adminorg.hospital1"]="AdminOrgHospital1MSP /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/adminorg.hospital1.com/users/Admin@adminorg.hospital1.com/msp peer0.adminorg.hospital1.com:7051 /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/adminorg.hospital1.com/peers/peer0.adminorg.hospital1.com/tls/ca.crt"
  ["cli.patientorg.hospital1"]="PatientOrgHospital1MSP /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/patientorg.hospital1.com/users/Admin@patientorg.hospital1.com/msp peer0.patientorg.hospital1.com:9051 /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/patientorg.hospital1.com/peers/peer0.patientorg.hospital1.com/tls/ca.crt"
  ["cli.doctororg.hospital1"]="DoctorOrgHospital1MSP /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/doctororg.hospital1.com/users/Admin@doctororg.hospital1.com/msp peer0.doctororg.hospital1.com:10051 /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/doctororg.hospital1.com/peers/peer0.doctororg.hospital1.com/tls/ca.crt"
  ["cli.peer1.doctororg.hospital1"]="DoctorOrgHospital1MSP /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/doctororg.hospital1.com/users/Admin@doctororg.hospital1.com/msp peer1.doctororg.hospital1.com:11051 /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/doctororg.hospital1.com/peers/peer1.doctororg.hospital1.com/tls/ca.crt"
)

for CLI in "${!CLI_ENV[@]}"; do
  IFS=' ' read -r MSP MSP_PATH PEER_ADDRESS TLS_CERT <<< "${CLI_ENV[$CLI]}"

  echo "🔐 Approving chaincode for $MSP via $CLI..."

  docker exec $CLI peer lifecycle chaincode approveformyorg \
    --channelID $CHANNEL_NAME \
    --name $CHAINCODE_NAME \
    --version $CHAINCODE_VERSION \
    --sequence $CHAINCODE_SEQUENCE \
    --package-id $PACKAGE_ID \
    $INIT_REQUIRED \
    --orderer $ORDERER_ADDRESS \
    --ordererTLSHostnameOverride $ORDERER_TLS_OVERRIDE \
    --tls \
    --cafile $ORDERER_TLS_CA \
    --peerAddresses $PEER_ADDRESS \
    --tlsRootCertFiles $TLS_CERT
done

echo "✅ Chaincode '$CHAINCODE_NAME' approved by all peers for '$CHANNEL_NAME'."
