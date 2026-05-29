# PostgreSQL Runbook

## Files

- Compose file: `docker-compose_postgres.yaml`
- Environment file: `.env.postgres`
- Host data directory: `POSTGRES_DATA_DIR` from `.env.postgres`

## Start

```powershell
docker-compose -f docker-compose_postgres.yaml --env-file .env.postgres up -d
```

## Stop

```powershell
docker-compose -f docker-compose_postgres.yaml --env-file .env.postgres down
```

## Validate Configuration

```powershell
docker-compose -f docker-compose_postgres.yaml --env-file .env.postgres config --quiet
```

## Useful Commands

```powershell
docker-compose -f docker-compose_postgres.yaml --env-file .env.postgres ps
docker-compose -f docker-compose_postgres.yaml --env-file .env.postgres logs -f postgres
docker inspect postgres-server-octadim
docker exec -it postgres-server-octadim psql -U <POSTGRES_USER> -d <POSTGRES_DB_NAME>
docker exec postgres-server-octadim pg_isready -h 127.0.0.1 -U <POSTGRES_USER> -d <POSTGRES_DB_NAME>
docker exec postgres-server-octadim pg_dump -U <POSTGRES_USER> <POSTGRES_DB_NAME> > postgres_backup.sql
Get-Content .\postgres_backup.sql | docker exec -i postgres-server-octadim psql -U <POSTGRES_USER> -d <POSTGRES_DB_NAME>
```

## Notes

- Run commands from the `docker_compose` directory.
- Use `--env-file .env.postgres`; the shared `.env` file is deprecated.
- PostgreSQL data is bind-mounted from `POSTGRES_DATA_DIR`, not stored in a Docker named volume.
- `docker-compose down -v` does not delete files stored in `POSTGRES_DATA_DIR`.
- On Windows Docker Desktop, ensure `POSTGRES_DATA_DIR` is valid for the active Docker engine context.
