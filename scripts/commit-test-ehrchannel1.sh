#!/bin/bash

set -e

CHANNEL_NAME="ehrchannel1"
CHAINCODE_NAME="test"
CHAINCODE_VERSION="1"
CHAINCODE_SEQUENCE="1"
INIT_REQUIRED="--init-required"

ORDERER_ADDRESS="orderer1.example.com:7050"
ORDERER_TLS_CA="/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer1.example.com/msp/tlscacerts/tlsca.example.com-cert.pem"
ORDERER_TLS_OVERRIDE="orderer1.example.com"

# Peer connection parameters
PEER_CONN_PARAMS=(
  --peerAddresses peer0.adminorg.hospital1.com:7051
  --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/adminorg.hospital1.com/peers/peer0.adminorg.hospital1.com/tls/ca.crt

  --peerAddresses peer0.patientorg.hospital1.com:9051
  --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/patientorg.hospital1.com/peers/peer0.patientorg.hospital1.com/tls/ca.crt

  --peerAddresses peer0.doctororg.hospital1.com:10051
  --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/doctororg.hospital1.com/peers/peer0.doctororg.hospital1.com/tls/ca.crt

  --peerAddresses peer1.doctororg.hospital1.com:11051
  --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/doctororg.hospital1.com/peers/peer1.doctororg.hospital1.com/tls/ca.crt
)

echo "📝 Committing chaincode '$CHAINCODE_NAME' to channel '$CHANNEL_NAME'..."

docker exec cli.adminorg.hospital1 peer lifecycle chaincode commit \
  --channelID $CHANNEL_NAME \
  --name $CHAINCODE_NAME \
  --version $CHAINCODE_VERSION \
  --sequence $CHAINCODE_SEQUENCE \
  $INIT_REQUIRED \
  --orderer $ORDERER_ADDRESS \
  --ordererTLSHostnameOverride $ORDERER_TLS_OVERRIDE \
  --tls \
  --cafile $ORDERER_TLS_CA \
  "${PEER_CONN_PARAMS[@]}"

echo "✅ Chaincode '$CHAINCODE_NAME' committed successfully on '$CHANNEL_NAME'."
