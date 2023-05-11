HOST="143.42.142.43"
USER="root"

DOCKER_HOST="ssh://${USER}@${HOST}" docker compose --verbose down
DOCKER_HOST="ssh://${USER}@${HOST}" docker compose --verbose up -d --build
DOCKER_HOST="ssh://${USER}@${HOST}" docker compose --verbose exec web python create_test_database.py
