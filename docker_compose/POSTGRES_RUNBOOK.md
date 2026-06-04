# PostgreSQL Runbook

## Files

- Local compose file: `local_docker-compose_postgres.yaml`
- Local environment file: `.env_local_postgres`
- IP-bound compose file: `ip_docker-compose_postgres.yaml`
- IP-bound environment file: `.env.ip_postgres`
- Host data directory: `POSTGRES_DATA_DIR` from the selected environment file

## Local Start

```powershell
docker-compose -f local_docker-compose_postgres.yaml --env-file .env_local_postgres up -d
```

## Local Stop

```powershell
docker-compose -f local_docker-compose_postgres.yaml --env-file .env_local_postgres down
```

## IP-Bound Start

```powershell
docker-compose -f ip_docker-compose_postgres.yaml --env-file .env.ip_postgres up -d
```

## IP-Bound Stop

```powershell
docker-compose -f ip_docker-compose_postgres.yaml --env-file .env.ip_postgres down
```

## Validate Configuration

```powershell
docker-compose -f local_docker-compose_postgres.yaml --env-file .env_local_postgres config --quiet
docker-compose -f ip_docker-compose_postgres.yaml --env-file .env.ip_postgres config --quiet
```

## Access

- Local host: `POSTGRES_HOST=127.0.0.1` from `.env_local_postgres`
- IP-bound host: `POSTGRES_HOST=176.124.136.22` from `.env.ip_postgres`
- Port: value of `POSTGRES_PORT` from the selected environment file
- Database: value of `POSTGRES_DB_NAME` from the selected environment file
- Username: value of `POSTGRES_USER` from the selected environment file
- Password: value of `POSTGRES_PASSWORD` from the selected environment file
- SSL: disabled for these local-development compose stacks

## Useful Commands

```powershell
docker-compose -f local_docker-compose_postgres.yaml --env-file .env_local_postgres ps
docker-compose -f local_docker-compose_postgres.yaml --env-file .env_local_postgres logs -f postgres
docker-compose -f ip_docker-compose_postgres.yaml --env-file .env.ip_postgres ps
docker-compose -f ip_docker-compose_postgres.yaml --env-file .env.ip_postgres logs -f postgres
docker exec local-postgres-server-octadim psql --version
docker exec local-postgres-server-octadim pg_isready -h 127.0.0.1 -U <POSTGRES_USER> -d <POSTGRES_DB_NAME>
docker exec ip-postgres-server-octadim psql --version
docker exec ip-postgres-server-octadim pg_isready -h 127.0.0.1 -U <POSTGRES_USER> -d <POSTGRES_DB_NAME>
```

## Notes

- Run commands from the `docker_compose` directory.
- Use the local pair only for loopback access on `127.0.0.1`.
- Use the IP-bound pair only on a host that actually owns `176.124.136.22`; Docker cannot bind to an address missing from the host network interfaces.
- PostgreSQL data is bind-mounted from `POSTGRES_DATA_DIR`, not stored in a Docker named volume.
- `docker-compose down -v` does not delete files stored in `POSTGRES_DATA_DIR`.
- Replace placeholder secrets in the selected `.env.*.postgres` file before real use.
- The PostgreSQL entrypoint wrapper verifies that `psql` and `pg_isready` exist
  in the selected image before it delegates to the official PostgreSQL
  entrypoint. This keeps client-tool availability part of the startup contract.
