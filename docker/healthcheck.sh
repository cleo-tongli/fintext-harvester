#!/usr/bin/env bash
set -e
LAST_FILE=$(find /app/data/bronze -type f -mmin -30 2>/dev/null | head -n1 || true)
if [ -n "$LAST_FILE" ]; then
  echo "OK recent file: $LAST_FILE"
  exit 0
else
  echo "No fresh bronze files in last 30 minutes"
  exit 1
fi
