#!/bin/bash

# Build AWS Lambda deployment package for V-JEPA-2 API

set -e

echo "🚀 Building AWS Lambda deployment package..."

# Set variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LAMBDA_DIR="$PROJECT_ROOT/deployments/lambda"
BUILD_DIR="$PROJECT_ROOT/build"
PACKAGE_NAME="vjepa2-lambda.zip"

# Create build directory
mkdir -p "$BUILD_DIR"

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required but not installed"
    exit 1
fi

echo "📦 Building Lambda package with Docker..."

# Build the Lambda package using Docker
docker build \
    -f "$LAMBDA_DIR/Dockerfile" \
    -t vjepa2-lambda-builder \
    "$PROJECT_ROOT"

# Extract the package from the container
CONTAINER_ID=$(docker create vjepa2-lambda-builder)
docker cp "$CONTAINER_ID:/lambda-package.zip" "$BUILD_DIR/$PACKAGE_NAME"
docker rm "$CONTAINER_ID"

# Check if package was created successfully
if [ -f "$BUILD_DIR/$PACKAGE_NAME" ]; then
    PACKAGE_SIZE=$(du -h "$BUILD_DIR/$PACKAGE_NAME" | cut -f1)
    echo "✅ Lambda package created successfully!"
    echo "📁 Package location: $BUILD_DIR/$PACKAGE_NAME"
    echo "📏 Package size: $PACKAGE_SIZE"
    
    # Check package size (Lambda has 250MB limit)
    PACKAGE_SIZE_BYTES=$(stat -f%z "$BUILD_DIR/$PACKAGE_NAME" 2>/dev/null || stat -c%s "$BUILD_DIR/$PACKAGE_NAME" 2>/dev/null)
    PACKAGE_SIZE_MB=$((PACKAGE_SIZE_BYTES / 1024 / 1024))
    
    if [ $PACKAGE_SIZE_MB -gt 250 ]; then
        echo "⚠️  Warning: Package size ($PACKAGE_SIZE_MB MB) exceeds Lambda's 250MB limit"
        echo "💡 Consider using container images instead of .zip packages"
    else
        echo "✅ Package size is within Lambda limits"
    fi
else
    echo "❌ Failed to create Lambda package"
    exit 1
fi

echo ""
echo "🎯 Next steps:"
echo "1. Deploy to Lambda:"
echo "   aws lambda create-function \\"
echo "     --function-name vjepa2-analyzer \\"
echo "     --runtime provided.al2023 \\"
echo "     --handler handler.lambda_handler \\"
echo "     --architectures arm64 \\"
echo "     --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-execution-role \\"
echo "     --zip-file fileb://$BUILD_DIR/$PACKAGE_NAME"
echo ""
echo "2. Or update existing function:"
echo "   aws lambda update-function-code \\"
echo "     --function-name vjepa2-analyzer \\"
echo "     --zip-file fileb://$BUILD_DIR/$PACKAGE_NAME" 