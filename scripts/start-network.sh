#!/bin/bash

# Stop on first error
set -e

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
  echo "❌ Docker is not running. Please start Docker and try again."
  exit 1
fi

# Navigate to docker folder
cd "$(dirname "$0")/../docker"

echo "⏳ Bringing up Hyperledger Fabric network using docker-compose.yaml..."

# Start the network in detached mode
docker-compose -f docker-compose.yaml up -d

# Check if docker-compose succeeded
if [ $? -ne 0 ]; then
  echo "❌ Docker network failed to start."
  exit 1
fi

echo "✅ Network started successfully!"

# Optional: Show running containers
echo ""
echo "📦 Running Docker containers:"
docker ps --filter "name=orderer" --filter "name=peer" --filter "name=cli"

echo ""
echo "🪵 Tip: View logs with: docker-compose -f docker-compose.yaml logs -f"
echo "🧠 Tip: Use ./scripts/join-channel1.sh to join peers to channels."
