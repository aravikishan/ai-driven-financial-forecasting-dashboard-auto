#!/bin/bash
set -e
echo "Starting AI-Driven Financial Forecasting Dashboard..."
uvicorn app:app --host 0.0.0.0 --port 9031 --workers 1
