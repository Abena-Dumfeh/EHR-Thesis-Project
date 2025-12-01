#!/bin/bash
set -e

echo "🔗 Checking all peer channel memberships..."

PEERS=(
  "cli.adminorg.hospital1"
  "cli.patientorg.hospital1"
  "cli.doctororg.hospital1"
)

for peer in "${PEERS[@]}"; do
  echo "🔍 Checking channels for $peer..."
  
  if docker ps --format '{{.Names}}' | grep -q "^${peer}$"; then
    docker exec "$peer" peer channel list || echo "⚠️ Could not query $peer"
  else
    echo "❌ $peer is not running"
  fi

  echo "----------------------------------"
done

echo "✅ Channel check complete."
