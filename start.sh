#!/bin/bash
set -e
echo "Starting Decentralized Identity Verification System..."
uvicorn app:app --host 0.0.0.0 --port 9008 --workers 1
