#!/bin/bash

# Load variables from .env
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo "Missing .env file!"
  exit 1
fi

TARGET_DIR="./server"

echo "Downloading GeoLite2-City..."
curl -O -J -L -u "$ACCOUNT_ID:$LICENSE_KEY" "https://download.maxmind.com/geoip/databases/GeoLite2-City/download?suffix=tar.gz"

echo "Extracting database..."
tar -xzf GeoLite2-City_*.tar.gz

echo "Finding the .mmdb file..."
mmdb_file=$(find . -name "*.mmdb" | head -n 1)

if [ -z "$mmdb_file" ]; then
  echo "Error: .mmdb file not found after extraction."
  exit 1
fi

echo "Found the .mmdb file..."
echo "Moving the .mmdb file..."

mv "$mmdb_file" "${TARGET_DIR}/GeoLite2-City.mmdb"

echo "Cleaning up..."
rm GeoLite2-City_*.tar.gz
rm -r GeoLite2-City_*

echo "GeoLite2-City.mmdb update complete!"