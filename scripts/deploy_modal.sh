#!/bin/bash

# Deploy V-JEPA-2 API to Modal Labs

set -e

echo "🚀 Deploying V-JEPA-2 API to Modal Labs..."

# Set variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MODAL_DIR="$PROJECT_ROOT/deployments/modal"

# Check if Modal CLI is installed
if ! command -v modal &> /dev/null; then
    echo "❌ Modal CLI is not installed"
    echo "💡 Install it with: pip install modal"
    exit 1
fi

# Check if user is authenticated
if ! modal token list &> /dev/null; then
    echo "❌ Not authenticated with Modal"
    echo "💡 Run: modal token new"
    exit 1
fi

echo "📦 Deploying to Modal..."

# Change to Modal directory
cd "$MODAL_DIR"

# Deploy the application
echo "🔧 Building and deploying Modal app..."
modal deploy app.py

echo ""
echo "✅ Modal deployment completed!"
echo ""
echo "🎯 Your Modal endpoints:"
echo "   - Health check: modal app vjepa2-api health-endpoint"
echo "   - Analysis: modal app vjepa2-api analyze-endpoint"
echo ""
echo "🌐 To get the public URLs:"
echo "   modal app vjepa2-api"
echo ""
echo "🔍 To view logs:"
echo "   modal logs vjepa2-api" 