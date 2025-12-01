#!/bin/bash

# Stop on first error
set -e

# Navigate to the docker folder
cd "$(dirname "$0")/../docker"

echo "🛑 Stopping and removing all Fabric containers..."

# Bring the network down
docker-compose -f docker-compose.yaml down

echo "✅ Network stopped successfully."

# Optional: Clean up dangling volumes (only if you want to delete ledger data)
# Uncomment the next line to enable
# echo "🧹 Removing volumes..."
# docker volume prune -f

# Optional: Show remaining containers (for confirmation/debugging)
echo ""
echo "📦 Remaining Docker containers (if any):"
docker ps --filter "name=orderer" --filter "name=peer" --filter "name=cli"

echo ""
echo "🧠 Tip: Run ./scripts/start-network.sh to restart the network."
