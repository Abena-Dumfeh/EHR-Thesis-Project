#!/bin/bash
set -e

CHANNEL_NAME="ehrchannel1"
CHAINCODE_NAME="test"
CHAINCODE_VERSION="1"
CHAINCODE_SEQUENCE="2"
PACKAGE_ID="test_1:a0c8411d301fb28097e4c341007834b1b7801152e31af90082fb50d63fb2279d"

echo "🔐 Re-approving chaincode $CHAINCODE_NAME with --init-required..."

docker exec cli.adminorg.hospital1 \
  peer lifecycle chaincode approveformyorg \
  --channelID $CHANNEL_NAME \
  --name $CHAINCODE_NAME \
  --version $CHAINCODE_VERSION \
  --package-id $PACKAGE_ID \
  --sequence $CHAINCODE_SEQUENCE \
  --init-required \
  --tls \
  --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer1.example.com/msp/tlscacerts/tlsca.example.com-cert.pem \
  -o orderer1.example.com:7050 \
  --ordererTLSHostnameOverride orderer1.example.com

docker exec cli.patientorg.hospital1 \
  peer lifecycle chaincode approveformyorg \
  --channelID $CHANNEL_NAME \
  --name $CHAINCODE_NAME \
  --version $CHAINCODE_VERSION \
  --package-id $PACKAGE_ID \
  --sequence $CHAINCODE_SEQUENCE \
  --init-required \
  --tls \
  --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer1.example.com/msp/tlscacerts/tlsca.example.com-cert.pem \
  -o orderer1.example.com:7050 \
  --ordererTLSHostnameOverride orderer1.example.com

docker exec cli.doctororg.hospital1 \
  peer lifecycle chaincode approveformyorg \
  --channelID $CHANNEL_NAME \
  --name $CHAINCODE_NAME \
  --version $CHAINCODE_VERSION \
  --package-id $PACKAGE_ID \
  --sequence $CHAINCODE_SEQUENCE \
  --init-required \
  --tls \
  --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer1.example.com/msp/tlscacerts/tlsca.example.com-cert.pem \
  -o orderer1.example.com:7050 \
  --ordererTLSHostnameOverride orderer1.example.com

echo "📦 Committing chaincode..."

docker exec cli.adminorg.hospital1 \
  peer lifecycle chaincode commit \
  -o orderer1.example.com:7050 \
  --ordererTLSHostnameOverride orderer1.example.com \
  --channelID $CHANNEL_NAME \
  --name $CHAINCODE_NAME \
  --version $CHAINCODE_VERSION \
  --sequence $CHAINCODE_SEQUENCE \
  --init-required \
  --tls \
  --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer1.example.com/msp/tlscacerts/tlsca.example.com-cert.pem \
  --peerAddresses peer0.adminorg.hospital1.com:7051 \
  --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/adminorg.hospital1.com/peers/peer0.adminorg.hospital1.com/tls/ca.crt \
  --peerAddresses peer0.patientorg.hospital1.com:9051 \
  --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/patientorg.hospital1.com/peers/peer0.patientorg.hospital1.com/tls/ca.crt \
  --peerAddresses peer0.doctororg.hospital1.com:10051 \
  --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/doctororg.hospital1.com/peers/peer0.doctororg.hospital1.com/tls/ca.crt
