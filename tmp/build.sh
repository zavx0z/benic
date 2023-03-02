docker run -it --rm \
  -v /store/data:/var/lib/postgresql/data \
  -v /store/logs:/logs \
  -e POSTGRES_USER=zavx0zBenif \
  -e POSTGRES_PASSWORD=12112022 \
  -e POSTGRES_DB=benif \
  -e JWT_SECRET_KEY='adkngdfFDGSDFqhnlakjflorqirefOJ;SJDG' \
  -p 80:80 \
  -p 443:443 \
  -p 8000:8000 \
  zavx0z:benic

docker-compose run  --rm \
certbot certonly \
--webroot \
--webroot-path=/var/www/certbot \
--email you@example.com \
--agree-tos \
--no-eff-email \
-d \
your-domain.com


docker build -t zavx0z:benic .

docker run -it --rm \
-e POSTGRES_DB \
-e POSTGRES_HOST \
-e POSTGRES_PORT \
-e POSTGRES_USER \
-e POSTGRES_PASSWORD \
-e JWT_SECRET_KEY \
-e DOMAIN myimage


docker run -it --rm \
  -v /store/data:/var/lib/postgresql/data \
  -v /store/logs:/logs \
  -e POSTGRES_USER=zavx0zBenif \
  -e POSTGRES_PASSWORD=12112022 \
  -e POSTGRES_DB=benif \
  -e JWT_SECRET_KEY='adkngdfFDGSDFqhnlakjflorqirefOJ;SJDG' \
  -p 80:80 \
  -p 443:443 \
  -p 8000:8000 \
  zavx0z:benic