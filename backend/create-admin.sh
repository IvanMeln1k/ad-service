#!/bin/sh
set -e

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
  echo "Usage: $0 <email> <name> <password>"
  echo "Example: $0 admin@example.com Admin pass123"
  exit 1
fi

EMAIL_RAW="$1"
NAME_RAW="$2"
PASSWORD="$3"

PROFILER_DB_CONTAINER="${PROFILER_DB_CONTAINER:-backend-db-1}"
AUTHER_DB_CONTAINER="${AUTHER_DB_CONTAINER:-backend-auther-db-1}"

# Escape single quotes for SQL literals
EMAIL=$(printf "%s" "$EMAIL_RAW" | sed "s/'/''/g")
NAME=$(printf "%s" "$NAME_RAW" | sed "s/'/''/g")

USER_ID=$(python3 - <<'PY'
import uuid
print(str(uuid.uuid4()))
PY
)

PASSWORD_HASH=$(python3 - "$PASSWORD" <<'PY'
import hashlib
import sys
print(hashlib.sha256(sys.argv[1].encode()).hexdigest())
PY
)

echo "==> Checking if email already exists in profiler..."
EXISTS=$(docker exec "$PROFILER_DB_CONTAINER" psql -U postgres -d profiler_service -tAc \
  "SELECT 1 FROM user_emails WHERE email = '$EMAIL' LIMIT 1;" | tr -d '[:space:]')

if [ "$EXISTS" = "1" ]; then
  echo "FAILED: Email already exists in profiler: $EMAIL_RAW"
  exit 1
fi

echo "==> Creating profile + confirmed email + ADMIN role (no events)..."
docker exec "$PROFILER_DB_CONTAINER" psql -v ON_ERROR_STOP=1 -U postgres -d profiler_service -c \
  "BEGIN;
   INSERT INTO profiles (user_id, name, city, created_at) VALUES ('$USER_ID', '$NAME', NULL, NOW());
   INSERT INTO user_emails (user_id, email, confirmed_at) VALUES ('$USER_ID', '$EMAIL', NOW());
   INSERT INTO profile_roles (user_id, role, assigned_at) VALUES ('$USER_ID', 'ADMIN', NOW());
   COMMIT;"

echo "==> Creating auth credentials..."
docker exec "$AUTHER_DB_CONTAINER" psql -v ON_ERROR_STOP=1 -U postgres -d auth_service -c \
  "INSERT INTO user_auth (uid, password_hash, created_at, updated_at)
   VALUES ('$USER_ID', '$PASSWORD_HASH', NOW(), NOW());"

echo "==> Done!"
echo "    user_id: $USER_ID"
echo "    email:   $EMAIL_RAW"
echo "    role:    ADMIN"
echo "    email_confirmed: true"
