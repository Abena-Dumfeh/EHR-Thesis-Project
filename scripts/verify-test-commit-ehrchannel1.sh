#!/bin/bash

set -e

CHANNEL_NAME="ehrchannel1"
CHAINCODE_NAME="test"

declare -A CLIS=(
  ["cli.adminorg.hospital1"]="AdminOrgHospital1MSP"
  ["cli.patientorg.hospital1"]="PatientOrgHospital1MSP"
  ["cli.doctororg.hospital1"]="DoctorOrgHospital1MSP"
  ["cli.peer1.doctororg.hospital1"]="DoctorOrgHospital1MSP"
)

echo "🔍 Verifying committed chaincode '$CHAINCODE_NAME' on channel '$CHANNEL_NAME' for all peers..."

for CLI in "${!CLIS[@]}"; do
  MSP="${CLIS[$CLI]}"
  echo "🔸 Checking on $CLI ($MSP)..."

  docker exec "$CLI" peer lifecycle chaincode querycommitted \
    --channelID "$CHANNEL_NAME" \
    --name "$CHAINCODE_NAME"

  echo "-------------------------------------------"
done

echo "✅ Chaincode '$CHAINCODE_NAME' commit verification complete on '$CHANNEL_NAME'."
