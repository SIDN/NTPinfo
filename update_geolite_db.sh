#!/bin/bash

# Load variables from .env
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo "Missing .env file!"
  exit 1
fi

TARGET_DIR="./server"

download_and_extract() {
  DB_NAME=$1
  echo "Downloading ${DB_NAME}..."
  curl -O -J -L -u "$ACCOUNT_ID:$LICENSE_KEY" "https://download.maxmind.com/geoip/databases/${DB_NAME}/download?suffix=tar.gz"

  echo "Extracting ${DB_NAME}..."
  tar -xzf ${DB_NAME}_*.tar.gz

  EXTRACTED_DIR=$(tar -tzf ${DB_NAME}_*.tar.gz | head -1 | cut -f1 -d"/")
  MMDB_FILE=$(find "$EXTRACTED_DIR" -name "*.mmdb" | head -n 1)

  if [ -z "$MMDB_FILE" ]; then
    echo "Error: .mmdb file not found for ${DB_NAME}."
    exit 1
  fi

  echo "Moving .mmdb to ${TARGET_DIR}/${DB_NAME}.mmdb"
  mv "$MMDB_FILE" "${TARGET_DIR}/${DB_NAME}.mmdb"

  echo "Cleaning up..."
  rm ${DB_NAME}_*.tar.gz
  rm -r "$EXTRACTED_DIR"

  echo "${DB_NAME}.mmdb update complete!"
}

download_and_extract "GeoLite2-City"
download_and_extract "GeoLite2-Country"
download_and_extract "GeoLite2-ASN"