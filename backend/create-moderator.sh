#!/bin/sh
set -e

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
  echo "Usage: $0 <email> <name> <password>"
  echo "Example: $0 mod@example.com Moderator pass123"
  exit 1
fi

EMAIL="$1"
NAME="$2"
PASSWORD="$3"

REGISTRATOR_URL="${REGISTRATOR_URL:-http://localhost:8004}"
PROFILER_DB_CONTAINER="${PROFILER_DB_CONTAINER:-backend-db-1}"

echo "==> Registering user $EMAIL..."
RESP=$(curl -s -X POST "$REGISTRATOR_URL/api/v1/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"name\":\"$NAME\",\"password\":\"$PASSWORD\"}")

USER_ID=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['user_id'])" 2>/dev/null)

if [ -z "$USER_ID" ]; then
  echo "FAILED: $RESP"
  exit 1
fi

echo "==> User created: $USER_ID"
echo "==> Assigning MODERATOR role..."

docker exec "$PROFILER_DB_CONTAINER" psql -U postgres -d profiler_service -c \
  "INSERT INTO profile_roles (user_id, role, assigned_at) VALUES ('$USER_ID', 'MODERATOR', NOW()) ON CONFLICT DO NOTHING;"

echo "==> Done! $EMAIL is now a moderator (user_id: $USER_ID)"
