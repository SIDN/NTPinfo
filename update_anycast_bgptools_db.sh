#!/bin/bash

TARGET_DIR="./server"

download_anycast_db() {
  FILE_NAME=$1
  URL=$2

  echo "Updating ${FILE_NAME} from ${URL}..."

  # Remove the old files
  rm -f "${TARGET_DIR}/${FILE_NAME}"

  # Download them
  STATUS_CODE=$(curl -s -o "${TARGET_DIR}/${FILE_NAME}" -w "%{http_code}" "$URL")

  if [ "$STATUS_CODE" -ne 200 ]; then
    echo "Failed to download ${FILE_NAME} (HTTP $STATUS_CODE)"
    exit 1
  fi

  echo "${FILE_NAME} updated successfully"
}

download_anycast_db "anycast-v4-prefixes.txt" "https://raw.githubusercontent.com/bgptools/anycast-prefixes/master/anycatch-v4-prefixes.txt"
download_anycast_db "anycast-v6-prefixes.txt" "https://raw.githubusercontent.com/bgptools/anycast-prefixes/master/anycatch-v6-prefixes.txt"

echo "All anycast prefix files are up to date."