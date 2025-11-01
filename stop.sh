#!/bin/bash

# Stop script for LangGraph Reflection application

set -e

echo "🛑 Stopping LangGraph Reflection application..."

# Check if docker compose is available
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed or not in PATH"
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo "❌ Error: docker compose is not available"
    exit 1
fi

# Stop containers
docker compose down

echo "✅ LangGraph Reflection application stopped"

