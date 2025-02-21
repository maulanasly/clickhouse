# ClickHouse Service Management

Docker Compose based ClickHouse service management using Makefile.

## Prerequisites

- Docker and Docker Compose
- Python 3.11
- Dataset from [Kaggle - Transactions Fraud Datasets](https://www.kaggle.com/datasets/computingvictor/transactions-fraud-datasets)

## Quick Start

1. Download and extract the dataset to `./datasets`
2. Use the following commands to manage the service:

```sh
make start    # Start service
make stop     # Stop service
make restart  # Restart service
make logs     # View logs
make status   # Check status
make clean    # Remove service and volumes
make build    # Build service
make pull     # Pull latest images
```

## Notes
- Ensure Docker and Docker Compose are running
- Default configuration in `docker-compose.yml`
