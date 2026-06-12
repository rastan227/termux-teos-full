#!/bin/bash
certbot renew --quiet --nginx
docker-compose -f docker-compose.prod.yml restart nginx
echo "Certificates renewed at $(date)" >> /var/log/teos-certbot.log
