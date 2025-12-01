#!/bin/bash
set -e

# === Required Inputs ===
CHANNEL_NAME="ehrchannel2"
ORG_MSP=$1  # e.g., AdminOrgHospital1MSP
ORG_NAME=$2  # e.g., adminorg.hospital1.com
PEER_NAME=$3  # e.g., peer0.adminorg.hospital1.com
PORT=$4  # e.g., 7051
CLI_CONTAINER=$5  # e.g., cli.adminorg.hospital1

# === Static Paths ===
ORDERER_CA="/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer1.example.com/msp/tlscacerts/tlsca.example.com-cert.pem"
FABRIC_PATH="/opt/gopath/src/github.com/hyperledger/fabric/peer"
ANCHOR_TX="${ORG_MSP}anchors_${CHANNEL_NAME}.tx"

echo "🔄 Generating anchor peer update for $ORG_MSP on channel $CHANNEL_NAME..."

# Step 1: Fetch latest config block
docker exec "$CLI_CONTAINER" \
  peer channel fetch config "$FABRIC_PATH/channel-artifacts/config_block.pb" \
  -o orderer1.example.com:7050 \
  --ordererTLSHostnameOverride orderer1.example.com \
  -c "$CHANNEL_NAME" \
  --tls --cafile "$ORDERER_CA"

# Step 2: Decode to JSON
docker exec "$CLI_CONTAINER" bash -c "
  cd $FABRIC_PATH/channel-artifacts && \
  configtxlator proto_decode --input config_block.pb --type common.Block --output config_block.json && \
  jq .data.data[0].payload.data.config config_block.json > config.json"

# Step 3: Modify config to include anchor peer
docker exec "$CLI_CONTAINER" bash -c "
  jq '.channel_group.groups.Application.groups[\"$ORG_MSP\"].values += {
    \"AnchorPeers\": {
      \"mod_policy\": \"Admins\",
      \"value\": {
        \"anchor_peers\": [
          {
            \"host\": \"$PEER_NAME\",
            \"port\": $PORT
          }
        ]
      },
      \"version\": \"0\"
    }
  }' $FABRIC_PATH/channel-artifacts/config.json > $FABRIC_PATH/channel-artifacts/modified_config.json"

# Step 4: Encode, compute update
docker exec "$CLI_CONTAINER" bash -c "
  cd $FABRIC_PATH/channel-artifacts && \
  configtxlator proto_encode --input config.json --type common.Config --output config.pb && \
  configtxlator proto_encode --input modified_config.json --type common.Config --output modified_config.pb && \
  configtxlator compute_update --channel_id $CHANNEL_NAME --original config.pb --updated modified_config.pb --output anchor_update.pb"

# Step 5: Wrap update in envelope
docker exec "$CLI_CONTAINER" bash -c "
  cd $FABRIC_PATH/channel-artifacts && \
  configtxlator proto_decode --input anchor_update.pb --type common.ConfigUpdate --output anchor_update.json && \
  jq -n --argfile update anchor_update.json '{\"payload\":{\"header\":{\"channel_header\":{\"channel_id\":\"$CHANNEL_NAME\",\"type\":2}},\"data\":{\"config_update\":\$update}}}' > anchor_update_envelope.json && \
  configtxlator proto_encode --input anchor_update_envelope.json --type common.Envelope --output $ANCHOR_TX"

# Step 6: Apply update
docker exec -e CORE_PEER_LOCALMSPID="$ORG_MSP" \
  -e CORE_PEER_MSPCONFIGPATH="$FABRIC_PATH/crypto/peerOrganizations/$ORG_NAME/users/Admin@$ORG_NAME/msp" \
  -e CORE_PEER_ADDRESS="$PEER_NAME:$PORT" \
  -e CORE_PEER_TLS_ENABLED=true \
  -e CORE_PEER_TLS_ROOTCERT_FILE="$FABRIC_PATH/crypto/peerOrganizations/$ORG_NAME/peers/$PEER_NAME/tls/ca.crt" \
  "$CLI_CONTAINER" \
  peer channel update \
    -o orderer1.example.com:7050 \
    --ordererTLSHostnameOverride orderer1.example.com \
    -c "$CHANNEL_NAME" \
    -f "$FABRIC_PATH/channel-artifacts/$ANCHOR_TX" \
    --tls --cafile "$ORDERER_CA"

echo "✅ Anchor peer for $ORG_MSP updated successfully on $CHANNEL_NAME"
