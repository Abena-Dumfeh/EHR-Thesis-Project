#!/bin/bash

# Set the config path again (safe practice)
export FABRIC_CFG_PATH=$HOME/ehr/config

# Ensure channel-artifacts folder exists
mkdir -p $HOME/ehr/channel-artifacts

# Generate the genesis block
configtxgen -profile GenesisProfile -channelID system-channel -outputBlock $HOME/ehr/channel-artifacts/genesis.block

# Confirm
if [ $? -eq 0 ]; then
    echo "Genesis block created at ehr/channel-artifacts/genesis.block"
else
    echo "Failed to generate genesis block"
    exit 1
fi
