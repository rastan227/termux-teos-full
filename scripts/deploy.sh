#!/bin/bash
# Production deployment script for TEOS

set -e

echo "🚀 Starting TEOS deployment..."

# Load environment
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Pull latest code
echo "📦 Pulling latest code..."
git pull origin main

# Build Docker images
echo "🐳 Building Docker images..."
docker-compose build

# Run database migrations
echo "🗄️ Running migrations..."
docker-compose run --rm bot alembic upgrade head

# Run health check
echo "🏥 Running health checks..."
sleep 5
curl -f http://localhost:8000/health || exit 1

# Start services
echo "▶️ Starting services..."
docker-compose up -d

# Set webhook if needed
if [ "$USE_WEBHOOK" = "true" ]; then
    echo "🔗 Setting webhook..."
    curl -X POST "https://api.telegram.org/bot$BOT_TOKEN/setWebhook?url=$BOT_WEBHOOK_URL/webhook"
fi

echo "✅ Deployment completed successfully!"
