#!/bin/bash
# Quick setup script for Paste Server

set -e

echo "=== Paste Server - Quick Setup ==="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker"
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Generate secrets if .env doesn't exist
if [ ! -f deployment/.env ]; then
    echo "📝 Creating deployment/.env file..."

    # Generate session secret
    SESSION_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")

    # Prompt for password
    echo ""
    read -sp "Enter password for web interface: " PASSWORD
    echo ""
    read -sp "Confirm password: " PASSWORD_CONFIRM
    echo ""

    if [ "$PASSWORD" != "$PASSWORD_CONFIRM" ]; then
        echo "❌ Passwords don't match!"
        exit 1
    fi

    # Generate password hash
    PASSWORD_HASH=$(python3 -c "import bcrypt; print(bcrypt.hashpw('$PASSWORD'.encode(), bcrypt.gensalt(12)).decode())")

    # Create .env file
    cat > deployment/.env <<EOF
SESSION_SECRET=$SESSION_SECRET
PASSWORD_HASH=$PASSWORD_HASH
DOMAIN=localhost
EOF

    echo "✅ Configuration file created at deployment/.env"
else
    echo "ℹ️  Using existing deployment/.env file"
fi

echo ""
echo "🚀 Starting services with Docker Compose..."
docker-compose -f deployment/docker-compose.yml up -d --build

echo ""
echo "✅ Paste Server is running!"
echo ""
echo "📍 Access at: http://localhost"
echo ""
echo "To stop: docker-compose -f deployment/docker-compose.yml down"
echo "To view logs: docker-compose -f deployment/docker-compose.yml logs -f"
