#!/bin/sh
set -e

if [ -n "$DB_HOST" ]; then
    echo "Waiting for PostgreSQL..."
    python <<'EOF'
import os
import sys
import time

import psycopg

def wait_for_db() -> None:
    dbname = os.environ["POSTGRES_DB"]
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]
    host = os.environ.get("DB_HOST", "db")
    port = os.environ.get("DB_PORT", "5432")

    for _ in range(60):
        try:
            with psycopg.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port,
                connect_timeout=3,
            ):
                return
        except psycopg.OperationalError:
            time.sleep(1)

    sys.exit("Database is unavailable after 60 seconds.")

wait_for_db()
EOF

    echo "Running migrations..."
    python manage.py migrate --noinput
fi

if [ "$1" = "gunicorn" ]; then
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
fi

exec "$@"
