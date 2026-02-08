#!/bin/bash

# LILITH CLI wrapper for OpenClaw
# This script interfaces with the LILITH backend API

# Get the prompt from arguments or stdin
if [ $# -gt 0 ]; then
    PROMPT="$*"
else
    PROMPT=$(cat)
fi

# Call LILITH backend API
curl -s -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"$PROMPT\", \"session_id\": \"openclaw\"}" | \
  jq -r '.response // .message // .' 2>/dev/null || \
  echo "Error: Failed to get response from LILITH"