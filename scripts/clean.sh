#!/bin/bash

set -e

echo "🧹 Stopping all Fabric-related Docker containers (peers, orderers, CLIs)..."
docker ps -a --filter "name=peer" --filter "name=orderer" --filter "name=cli" --format "{{.ID}}" | xargs -r docker stop
docker ps -a --filter "name=peer" --filter "name=orderer" --filter "name=cli" --format "{{.ID}}" | xargs -r docker rm

echo "🗑 Removing all Docker volumes (including chaincode ledgers)..."
docker volume prune -f

echo "🧼 Deleting old crypto materials..."
rm -rf ../crypto-material/*

echo "🧼 Deleting old channel artifacts..."
rm -rf ../channel-artifacts/*

echo "🧼 (Optional) Clearing old chaincode containers..."
docker ps -a --filter "name=dev-peer" --format "{{.ID}}" | xargs -r docker rm

echo "🧼 (Optional) Removing old chaincode images..."
docker images --filter=reference='dev-peer*' --format "{{.ID}}" | xargs -r docker rmi -f

# Fix peer-ledgers folder ownership
if [ -d ../peer-ledgers/ ]; then
  echo "🔧 Fixing ownership of peer-ledgers..."
  sudo chown -R "$USER:$USER" ../peer-ledgers/
else
  echo "⚠️  peer-ledgers folder not found, skipping ownership fix"
fi

echo "✅ Clean complete. You can now restart the network using ./scripts/start-network.sh"
