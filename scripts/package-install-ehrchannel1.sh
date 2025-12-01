#!/bin/bash

set -e

# 👇 Change these to reflect your actual chaincode
CHAINCODE_NAME="ehr"
CHAINCODE_LABEL="ehr_7"
CHAINCODE_LANG="golang"
CHAINCODE_SRC_PATH="./chaincode/ehr/go"
PACKAGE_FILE="${CHAINCODE_LABEL}.tar.gz"

# ✅ Package chaincode
if [ ! -f "$PACKAGE_FILE" ]; then
  echo "📦 Packaging chaincode $CHAINCODE_NAME..."
  peer lifecycle chaincode package "$PACKAGE_FILE" \
    --path "$CHAINCODE_SRC_PATH" \
    --lang "$CHAINCODE_LANG" \
    --label "$CHAINCODE_LABEL"
else
  echo "👜 Using existing chaincode package: $PACKAGE_FILE"
fi

# 🛰️ Peers to install on
declare -A PEERS=(
  ["cli.adminorg.hospital1"]="peer0.adminorg.hospital1.com"
  ["cli.patientorg.hospital1"]="peer0.patientorg.hospital1.com"
  ["cli.doctororg.hospital1"]="peer0.doctororg.hospital1.com"
  ["cli.peer1.doctororg.hospital1"]="peer1.doctororg.hospital1.com"
)

for CLI in "${!PEERS[@]}"; do
  PEER_NAME="${PEERS[$CLI]}"
  echo "📥 Installing chaincode on $PEER_NAME via $CLI..."

  docker cp "$PACKAGE_FILE" "$CLI:/opt/gopath/src/github.com/hyperledger/fabric/peer/$PACKAGE_FILE"

  docker exec "$CLI" peer lifecycle chaincode install \
    "/opt/gopath/src/github.com/hyperledger/fabric/peer/$PACKAGE_FILE"
done

echo "✅ Chaincode '$CHAINCODE_NAME' installed on all peers for ehrchannel1."
