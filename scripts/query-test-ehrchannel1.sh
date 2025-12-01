#!/bin/bash

set -e

CHANNEL_NAME="ehrchannel1"
CHAINCODE_NAME="test"
QUERY_FUNCTION="GetAllAssets"

declare -A PEERS=(
  ["cli.adminorg.hospital1"]="peer0.adminorg.hospital1.com"
  ["cli.patientorg.hospital1"]="peer0.patientorg.hospital1.com"
  ["cli.doctororg.hospital1"]="peer0.doctororg.hospital1.com"
  ["cli.peer1.doctororg.hospital1"]="peer1.doctororg.hospital1.com"
)

echo "🔍 Querying '$QUERY_FUNCTION' from chaincode '$CHAINCODE_NAME' on '$CHANNEL_NAME'..."

for CLI in "${!PEERS[@]}"; do
  PEER_NAME="${PEERS[$CLI]}"
  echo "🔸 Querying $QUERY_FUNCTION on $PEER_NAME using $CLI..."

  docker exec "$CLI" peer chaincode query \
    -C "$CHANNEL_NAME" \
    -n "$CHAINCODE_NAME" \
    -c "{\"Args\":[\"$QUERY_FUNCTION\"]}"

  echo "-------------------------------------------"
done

echo "✅ Query complete for all peers on $CHANNEL_NAME."
