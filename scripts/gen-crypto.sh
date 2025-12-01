#!/bin/bash

# Set the path to your config files
export FABRIC_CFG_PATH=$HOME/ehr/config

# Remove old crypto material (optional but recommended)
rm -rf $HOME/ehr/crypto-material

# Generate new crypto materials
cryptogen generate --config=$FABRIC_CFG_PATH/crypto-config.yaml --output=$HOME/ehr/crypto-material

# Confirm
if [ $? -eq 0 ]; then
    echo "Crypto material generated successfully in ehr/crypto-material"
else
    echo "Failed to generate crypto material"
    exit 1
fi


# Patch: copy admincerts for each peer org
ORG_DIRS=$(find $HOME/ehr/crypto-material/peerOrganizations -maxdepth 1 -mindepth 1 -type d)

for ORG in $ORG_DIRS; do
  USER_MSP="$ORG/users/Admin@$(basename $ORG)/msp"
  SIGNCERT="$USER_MSP/signcerts/Admin@$(basename $ORG)-cert.pem"

  if [ -f "$SIGNCERT" ]; then
    mkdir -p "$USER_MSP/admincerts"
    cp "$SIGNCERT" "$USER_MSP/admincerts/"
    echo "✅ Patched admincert for $USER_MSP"
  else
    echo "⚠️ Signcert not found in $USER_MSP"
  fi
done
