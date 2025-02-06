# ClickHouse Service Management

This project uses a `Makefile` to manage the ClickHouse service with Docker Compose. Below are the available commands to start, stop, restart, view logs, check status, clean, build, and pull the latest images for the ClickHouse service.

## Prerequisites

- Docker
- Docker Compose

## Available Commands

### Start the ClickHouse Service

To start the ClickHouse service, run:

```sh
make start
```

### Stop the ClickHouse Service
To stop the ClickHouse service, run:

```sh
make stop
```

### Restart the ClickHouse Service
To restart the ClickHouse service, run:

```sh
make restart
```

### View Logs of the ClickHouse Service
To view the logs of the ClickHouse service, run:

```sh
make logs
```

### Check the Status of the ClickHouse Service
To check the status of the ClickHouse service, run:

```sh
make status
```

### Clean the ClickHouse Service
To remove the ClickHouse service and its volumes, run:

```sh
make clean
```


### Build the ClickHouse Service
To build the ClickHouse service (if needed), run:

```sh
make build
```

### Pull the Latest Images for the ClickHouse Service
To pull the latest images for the ClickHouse service, run:

```sh
make pull
```

### Notes
Ensure that Docker and Docker Compose are installed and running on your machine.
The Makefile uses docker-compose.yml as the Docker Compose file by default.