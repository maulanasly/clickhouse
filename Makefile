# Define the Docker Compose file
DOCKER_COMPOSE_FILE = docker-compose.yml

# Define the service name
SERVICE_NAME = clickhouse

# Target to start the ClickHouse service
start:
    docker compose -f $(DOCKER_COMPOSE_FILE) up -d

# Target to stop the ClickHouse service
stop:
    docker compose -f $(DOCKER_COMPOSE_FILE) down

# Target to restart the ClickHouse service
restart:
    docker compose -f $(DOCKER_COMPOSE_FILE) down
    docker compose -f $(DOCKER_COMPOSE_FILE) up -d

# Target to view the logs of the ClickHouse service
logs:
    docker compose -f $(DOCKER_COMPOSE_FILE) logs -f $(SERVICE_NAME)

# Target to check the status of the ClickHouse service
status:
    docker compose -f $(DOCKER_COMPOSE_FILE) ps

# Target to remove the ClickHouse service and its volumes
clean:
    docker compose -f $(DOCKER_COMPOSE_FILE) down -v

# Target to build the ClickHouse service (if needed)
build:
    docker compose -f $(DOCKER_COMPOSE_FILE) build

# Target to pull the latest images for the ClickHouse service
pull:
    docker compose -f $(DOCKER_COMPOSE_FILE) pull

iniitial-data:
    python3 ./scripts/dataset_importer.py --dataset=./datasets

.PHONY: start stop restart logs status clean build pull
