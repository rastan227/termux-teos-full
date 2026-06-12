#!/bin/bash
# Generate secure random secrets for .env

echo "# Generated secrets - $(date)" > .env.secrets
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env.secrets
echo "JWT_SECRET=$(openssl rand -hex 32)" >> .env.secrets
echo "REDIS_PASSWORD=$(openssl rand -hex 16)" >> .env.secrets
echo "DB_PASS=$(openssl rand -hex 16)" >> .env.secrets
echo "PAYMENT_WEBHOOK_SECRET=$(openssl rand -hex 24)" >> .env.secrets
echo "Generated .env.secrets - copy these to .env"
