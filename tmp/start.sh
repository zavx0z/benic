#!/bin/bash

# Получаем сертификат Let's Encrypt и настраиваем nginx
certbot certonly --noninteractive --agree-tos --email your-email@example.com -d your-domain.com --nginx
cp /etc/letsencrypt/options-ssl-nginx.conf /etc/nginx/options-ssl.conf
cp /etc/letsencrypt/ssl-dhparams.pem /etc/nginx/ssl-dhparams.pem
sed -i 's/# server_names_hash_bucket_size 64;/server_names_hash_bucket_size 64;/' /etc/nginx/nginx.conf

# Устанавливаем путь до файла сертификата
CERT_FILE="/etc/letsencrypt/live/your-domain.com/fullchain.pem"
KEY_FILE="/etc/letsencrypt/live/your-domain.com/privkey.pem"

# Настраиваем автоматическое обновление сертификата каждые 12 часов
crontab -l | { cat; echo "0 */12 * * * certbot renew --post-hook 'nginx -s reload' > /var/log/cron-letsencrypt-renew.log 2>&1"; } | crontab -

# Настраиваем nginx для работы с SSL
sed -i "s|<CERT_FILE>|$CERT_FILE|g" /etc/nginx/nginx.conf
sed -i "s|<KEY_FILE>|$KEY_FILE|g" /etc/nginx/nginx.conf


# Запускаем миграции
alembic upgrade head
# Запускаем Nginx
# Запускаем nginx и приложение
nginx -g "daemon off;"
# Запускаем приложение
uvicorn app.main:app --host 0.0.0.0 --port 8000
