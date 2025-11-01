#!/bin/bash

# Start script for LangGraph Reflection application

set -e

echo "🚀 Starting LangGraph Reflection application..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "📝 Creating .env from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file. Please edit it with your Azure OpenAI credentials."
        echo "   Edit .env file and run ./start.sh again."
        exit 1
    else
        echo "❌ Error: .env.example not found. Please create .env file manually."
        exit 1
    fi
fi

# Check if docker compose is available
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed or not in PATH"
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo "❌ Error: docker compose is not available"
    exit 1
fi

# Build and start containers
echo "🔨 Building Docker image..."
docker compose build

echo "🚀 Starting containers..."
docker compose up -d

# Wait for service to be ready
echo "⏳ Waiting for service to be ready..."
sleep 5

# Check if service is running
if docker compose ps | grep -q "Up"; then
    echo "✅ LangGraph Reflection application is running!"
    echo ""
    echo "📡 Access the application at:"
    echo "   - API: http://localhost:2024"
    echo "   - API Docs: http://localhost:2024/docs"
    echo "   - LangGraph Studio: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024"
    echo ""
    echo "📊 View logs with: docker compose logs -f"
    echo "🛑 Stop with: ./stop.sh"
else
    echo "❌ Error: Service failed to start"
    echo "📋 Check logs with: docker compose logs"
    exit 1
fi

