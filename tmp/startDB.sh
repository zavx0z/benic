SCRIPT_PATH=$(readlink -f "$0")
PARENT_DIR=$(dirname $(dirname "$SCRIPT_PATH"))
echo "$PARENT_DIR"
env_file="${PARENT_DIR}/.env"
store_dir=$(dirname "$PARENT_DIR")'/store/data'

export $(grep -E '^POSTGRES_PORT=' "${env_file}" | xargs)
export $(grep -E '^POSTGRES_DB=' "${env_file}" | xargs)
export $(grep -E '^POSTGRES_USER=' "${env_file}" | xargs)
export $(grep -E '^POSTGRES_PASSWORD=' "${env_file}" | xargs)

echo "POSTGRES_PORT = ${POSTGRES_PORT}"
echo "POSTGRES_DB = ${POSTGRES_DB}"
echo "POSTGRES_USER = ${POSTGRES_USER}"
echo "POSTGRES_PASSWORD = ${POSTGRES_PASSWORD}"

docker run --rm --detach \
  --name db \
  -p 5432:5432 \
  -v "${store_dir}:/var/lib/postgresql/data" \
  -e POSTGRES_PORT="${POSTGRES_PORT}" \
  -e POSTGRES_DB="${POSTGRES_DB}" \
  -e POSTGRES_USER="${POSTGRES_USER}" \
  -e POSTGRES_PASSWORD="${POSTGRES_PASSWORD}" \
  postgres:alpine
