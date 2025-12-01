#!/bin/bash

set -e

CHANNEL_NAME="ehrchannel1"
CHAINCODE_NAME="test"
ORDERER_ADDRESS="orderer1.example.com:7050"
ORDERER_TLS_CA="/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer1.example.com/msp/tlscacerts/tlsca.example.com-cert.pem"

echo "🚀 Invoking 'InitLedger' with --isInit on chaincode '$CHAINCODE_NAME'..."

docker exec cli.adminorg.hospital1 peer chaincode invoke \
  -o "$ORDERER_ADDRESS" \
  --ordererTLSHostnameOverride orderer1.example.com \
  --tls --cafile "$ORDERER_TLS_CA" \
  -C "$CHANNEL_NAME" \
  -n "$CHAINCODE_NAME" \
  --isInit \
  -c '{"Args":["InitLedger"]}' \
  --peerAddresses peer0.adminorg.hospital1.com:7051 \
    --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/adminorg.hospital1.com/peers/peer0.adminorg.hospital1.com/tls/ca.crt \
  --peerAddresses peer0.patientorg.hospital1.com:9051 \
    --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/patientorg.hospital1.com/peers/peer0.patientorg.hospital1.com/tls/ca.crt \
  --peerAddresses peer0.doctororg.hospital1.com:10051 \
    --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/doctororg.hospital1.com/peers/peer0.doctororg.hospital1.com/tls/ca.crt \
  --peerAddresses peer1.doctororg.hospital1.com:11051 \
    --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/doctororg.hospital1.com/peers/peer1.doctororg.hospital1.com/tls/ca.crt
