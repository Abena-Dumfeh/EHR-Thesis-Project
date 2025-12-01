#!/bin/bash
set -e

CHANNEL_NAME="ehrchannel2"
PROFILE_NAME="EHRChannel2Profile"
ORDERER_ADDRESS="orderer1.example.com:7050"
ORDERER_TLS_CA="/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer1.example.com/msp/tlscacerts/tlsca.example.com-cert.pem"
FABRIC_CFG_PATH="./config"

# List of orgs with their config
ORGS=(
  "AdminOrgHospital1MSP AdminOrgHospital1 adminorg.hospital1.com peer0.adminorg.hospital1.com 7051 cli.adminorg.hospital1"
  "PatientOrgHospital1MSP PatientOrgHospital1 patientorg.hospital1.com peer0.patientorg.hospital1.com 9051 cli.patientorg.hospital1"
  "DoctorOrgHospital1MSP DoctorOrgHospital1 doctororg.hospital1.com peer0.doctororg.hospital1.com 10051 cli.doctororg.hospital1"
  "AdminOrgHospital2MSP AdminOrgHospital2 adminorg.hospital2.com peer0.adminorg.hospital2.com 11051 cli.adminorg.hospital2"
  "DoctorOrgHospital2MSP DoctorOrgHospital2 doctororg.hospital2.com peer0.doctororg.hospital2.com 12051 cli.doctororg.hospital2"
)

for ORG_INFO in "${ORGS[@]}"; do
  read -r ORG_MSP AS_ORG_NAME ORG_DOMAIN PEER_HOST PEER_PORT CLI <<<"$ORG_INFO"
  TX_FILE="channel-artifacts/${ORG_MSP}anchors_${CHANNEL_NAME}.tx"
  TX_FILE_CONTAINER="/opt/gopath/src/github.com/hyperledger/fabric/peer/channel-artifacts/${ORG_MSP}anchors_${CHANNEL_NAME}.tx"

  echo "🔍 Checking if $ORG_MSP already has an anchor peer update..."
CURRENT_VERSION=$(docker exec "$CLI" bash -c "\
  peer channel fetch config config_block.pb -o $ORDERER_ADDRESS \
    --ordererTLSHostnameOverride orderer1.example.com \
    -c $CHANNEL_NAME --tls --cafile $ORDERER_TLS_CA && \
  configtxlator proto_decode --input config_block.pb --type common.Block | \
  jq '.data.data[0].payload.data.config.channel_group.groups.Application.groups[\"$AS_ORG_NAME\"] | .version'")

  if [[ "$CURRENT_VERSION" != "0" ]]; then
    echo "⚠️  Skipping $ORG_MSP: already updated (version $CURRENT_VERSION)."
    continue
  fi

  echo "🔄 Generating anchor peer update for $ORG_MSP..."
  ./bin/configtxgen \
    -profile "$PROFILE_NAME" \
    -outputAnchorPeersUpdate "$TX_FILE" \
    -channelID "$CHANNEL_NAME" \
    -asOrg "$AS_ORG_NAME"

  echo "📁 Copying TX to $CLI container..."
  docker cp "$TX_FILE" "$CLI:$TX_FILE_CONTAINER"

  echo "🖋️ Signing anchor peer TX with three orgs..."

  for SIGNER in \
    "AdminOrgHospital1MSP adminorg.hospital1.com peer0.adminorg.hospital1.com 7051 cli.adminorg.hospital1" \
    "PatientOrgHospital1MSP patientorg.hospital1.com peer0.patientorg.hospital1.com 9051 cli.patientorg.hospital1" \
    "DoctorOrgHospital1MSP doctororg.hospital1.com peer0.doctororg.hospital1.com 10051 cli.doctororg.hospital1"
  do
    read -r SIGNER_MSP SIGNER_DOMAIN SIGNER_PEER SIGNER_PORT SIGNER_CLI <<<"$SIGNER"

    docker exec \
      -e CORE_PEER_LOCALMSPID="$SIGNER_MSP" \
      -e CORE_PEER_MSPCONFIGPATH="/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/$SIGNER_DOMAIN/users/Admin@$SIGNER_DOMAIN/msp" \
      -e CORE_PEER_ADDRESS="$SIGNER_PEER:$SIGNER_PORT" \
      -e CORE_PEER_TLS_ENABLED=true \
      -e CORE_PEER_TLS_ROOTCERT_FILE="/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/$SIGNER_DOMAIN/peers/$SIGNER_PEER/tls/ca.crt" \
      "$SIGNER_CLI" \
      peer channel signconfigtx -f "$TX_FILE_CONTAINER"
  done

  echo "🚀 Submitting anchor peer update for $ORG_MSP..."
  docker exec \
    -e CORE_PEER_LOCALMSPID="$ORG_MSP" \
    -e CORE_PEER_MSPCONFIGPATH="/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/$ORG_DOMAIN/users/Admin@$ORG_DOMAIN/msp" \
    -e CORE_PEER_ADDRESS="$PEER_HOST:$PEER_PORT" \
    -e CORE_PEER_TLS_ENABLED=true \
    -e CORE_PEER_TLS_ROOTCERT_FILE="/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/$ORG_DOMAIN/peers/$PEER_HOST/tls/ca.crt" \
    "$CLI" \
    peer channel update \
      -o "$ORDERER_ADDRESS" \
      --ordererTLSHostnameOverride orderer1.example.com \
      -c "$CHANNEL_NAME" \
      -f "$TX_FILE_CONTAINER" \
      --tls \
      --cafile "$ORDERER_TLS_CA"

  echo "✅ Anchor peer updated for $ORG_MSP."
done

echo "🎉 All anchor peer updates attempted for channel '$CHANNEL_NAME'."
