#!/bin/bash
set -e
# Replace DOMAIN variable in nginx.conf with the value of the environment variable DOMAIN
sed -i "s/\${DOMAIN}/${DOMAIN}/g" /etc/nginx/conf.d/nginx.conf
# Start nginx
nginx -g "daemon off;"
