#!/bin/bash
# Development environment setup

echo "🔧 Setting up TEOS development environment..."

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -e ".[dev]"

# Setup pre-commit
pre-commit install

# Create .env from example if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️ Please edit .env file with your settings"
fi

# Initialize database
alembic upgrade head

# Run sample data seeding
python scripts/seed_data.py

echo "✅ Development environment ready!"
echo "Run 'docker-compose up' or 'python -m app.main' to start"
