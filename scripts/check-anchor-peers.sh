#!/bin/bash

set -e

# Optional: override orderer via first argument
ORDERER=${1:-orderer1.example.com:7050}

# Required tools check
command -v configtxlator >/dev/null || { echo "❌ configtxlator not found. Please install it."; exit 1; }
command -v jq >/dev/null || { echo "❌ jq not found. Please install it."; exit 1; }

CHANNEL="ehrchannel1"
PEER_CLI=cli.adminorg.hospital1
TLS_CA_IN_CONTAINER=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer1.example.com/msp/tlscacerts/tlsca.example.com-cert.pem
OUTPUT_DIR=./scripts/tmp-config

mkdir -p "$OUTPUT_DIR"

echo "📡 Checking anchor peers for channel: $CHANNEL"

# Fetch latest config block from the CLI container
docker exec $PEER_CLI peer channel fetch config "/tmp/${CHANNEL}_config_block.pb" \
  -o "$ORDERER" -c "$CHANNEL" --tls --cafile "$TLS_CA_IN_CONTAINER"

# Copy config block to host
docker cp "$PEER_CLI:/tmp/${CHANNEL}_config_block.pb" "$OUTPUT_DIR/${CHANNEL}_config_block.pb"

# Decode to JSON
configtxlator proto_decode --input "$OUTPUT_DIR/${CHANNEL}_config_block.pb" \
  --type common.Block --output "$OUTPUT_DIR/${CHANNEL}_config_block.json"

# Print anchor peers using jq
echo "🔍 Anchor peers in $CHANNEL:"
cat "$OUTPUT_DIR/${CHANNEL}_config_block.json" | jq '
  .data.data[0].payload.data.config.channel_group.groups.Application.groups
  | to_entries[]
  | {org: .key, anchor_peers: .value.values.AnchorPeers.value.anchor_peers}
'
echo "-------------------------------------------"

# Optional cleanup
# echo "🧹 Cleaning up temporary files..."
# rm -rf "$OUTPUT_DIR"

echo "✅ Anchor peer check complete for $CHANNEL."
