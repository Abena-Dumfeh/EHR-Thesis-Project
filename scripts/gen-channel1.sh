#!/bin/bash

echo "Generating ehrchannel1 artifacts for Hospital1..."

CHANNEL_ARTIFACTS="$(cd "$(dirname "$0")/../channel-artifacts" && pwd)"
#CONFIG_PATH=../config
CONFIG_PATH="$(cd "$(dirname "$0")/../config" && pwd)"

export FABRIC_CFG_PATH=$CONFIG_PATH

# ----- Channel 1: ehrchannel1 -----
configtxgen -profile EHRChannel1Profile -channelID ehrchannel1 \
  -configPath $CONFIG_PATH \
  -outputCreateChannelTx $CHANNEL_ARTIFACTS/ehrchannel1.tx

# -------- Anchor Peers for Hospital1 Orgs --------
configtxgen -profile EHRChannel1Profile -channelID ehrchannel1 \
  -configPath $CONFIG_PATH \
  -outputAnchorPeersUpdate $CHANNEL_ARTIFACTS/AdminOrgHospital1MSPanchors_ehrchannel1.tx -asOrg AdminOrgHospital1
#  -outputAnchorPeersUpdate $CHANNEL_ARTIFACTS/AdminOrgHospital1MSPanchors.tx -asOrg AdminOrgHospital1

configtxgen -profile EHRChannel1Profile -channelID ehrchannel1 \
  -configPath $CONFIG_PATH \
  -outputAnchorPeersUpdate $CHANNEL_ARTIFACTS/PatientOrgHospital1MSPanchors_ehrchannel1.tx -asOrg PatientOrgHospital1
#  -outputAnchorPeersUpdate $CHANNEL_ARTIFACTS/PatientOrgHospital1MSPanchors.tx -asOrg PatientOrgHospital1

configtxgen -profile EHRChannel1Profile -channelID ehrchannel1 \
  -configPath $CONFIG_PATH \
  -outputAnchorPeersUpdate $CHANNEL_ARTIFACTS/DoctorOrgHospital1MSPanchors_ehrchannel1.tx -asOrg DoctorOrgHospital1
#  -outputAnchorPeersUpdate $CHANNEL_ARTIFACTS/DoctorOrgHospital1MSPanchors.tx -asOrg DoctorOrgHospital1

echo "✅ Channel ehrchannel1 and anchor peer artifacts created in $CHANNEL_ARTIFACTS"
