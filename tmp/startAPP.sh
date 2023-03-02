SCRIPT_PATH=$(readlink -f "$0")
PARENT_DIR=$(dirname $(dirname "$SCRIPT_PATH"))
echo "$PARENT_DIR"
env_file="${PARENT_DIR}/.env"
store_dir=$(dirname "$PARENT_DIR")'/store/data'

export $(grep -E '^POSTGRES_PORT=' "${env_file}" | xargs)
export $(grep -E '^POSTGRES_DB=' "${env_file}" | xargs)
export $(grep -E '^POSTGRES_USER=' "${env_file}" | xargs)
export $(grep -E '^POSTGRES_PASSWORD=' "${env_file}" | xargs)
export $(grep -E '^POSTGRES_HOST=' "${env_file}" | xargs)
export $(grep -E '^JWT_SECRET_KEY=' "${env_file}" | xargs)

echo "POSTGRES_DB = ${POSTGRES_DB}"
echo "POSTGRES_PORT = ${POSTGRES_PORT}"
echo "POSTGRES_USER = ${POSTGRES_USER}"
echo "POSTGRES_PASSWORD = ${POSTGRES_PASSWORD}"
echo "JWT_SECRET_KEY = ${JWT_SECRET_KEY}"

#  --rm \
#  --detach \
docker run \
  --name app \
  -e POSTGRES_HOST="db" \
  -e POSTGRES_PORT="${POSTGRES_PORT}" \
  -e POSTGRES_DB="${POSTGRES_DB}" \
  -e POSTGRES_USER="${POSTGRES_USER}" \
  -e POSTGRES_PASSWORD="${POSTGRES_PASSWORD}" \
  -e JWT_SECRET_KEY="${JWT_SECRET_KEY}" \
  -p 8080:8000 \
  zavx0z:benic
