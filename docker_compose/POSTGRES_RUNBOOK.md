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

## Connect from Windows DBeaver

This stack is safe to use from DBeaver installed on Windows when Docker runs the
PostgreSQL container inside WSL. The compose file publishes container port
`5432` to `${POSTGRES_HOST:-127.0.0.1}:${POSTGRES_PORT:-5432}` from
`.env.postgres`. In WSL2 mirrored networking mode, prefer a non-default host
port such as `15432` when Windows or Ubuntu already has a local PostgreSQL
server on `5432`.

Use these DBeaver connection settings:

- Driver: PostgreSQL
- Host: value of `POSTGRES_HOST` from `.env.postgres`, usually `127.0.0.1`
- Port: value of `POSTGRES_PORT` from `.env.postgres`, usually `15432` in this
  WSL workspace
- Database: value of `POSTGRES_DB_NAME` from `.env.postgres`
- Username: value of `POSTGRES_USER` from `.env.postgres`
- Password: value of `POSTGRES_PASSWORD` from `.env.postgres`
- SSL: disabled for the local compose stack

If DBeaver cannot connect, first confirm that Docker actually published the
host port:

```powershell
docker port postgres-server-octadim
docker inspect postgres-server-octadim
```

The expected `docker port` output should include a mapping similar to:

```text
5432/tcp -> 127.0.0.1:15432
```

If the container is healthy but no host port is published, recreate the
container from the current compose file and env file:

```powershell
docker-compose -f docker-compose_postgres.yaml --env-file .env.postgres up -d --force-recreate
docker port postgres-server-octadim
```

If Windows PostgreSQL or Ubuntu PostgreSQL also uses `5432`, keep this compose
stack on a separate host port:

```text
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=15432
```

Then use `127.0.0.1:15432` in DBeaver. This avoids DBeaver accidentally
connecting to the Windows or Ubuntu PostgreSQL instance instead of the Docker
container.

If Windows cannot reach `127.0.0.1`, use a WSL fallback:

1. Set `POSTGRES_HOST=0.0.0.0` in `.env.postgres`.
2. Recreate the container with the command above.
3. Get the WSL address with `hostname -I` inside WSL.
4. Use that WSL address as the DBeaver host with the same PostgreSQL port.

### DBeaver `no pg_hba.conf entry ... no encryption`

If DBeaver shows an error similar to:

```text
FATAL: no pg_hba.conf entry for host "...", user "...", database "...", no encryption
```

first verify that DBeaver is connected to this compose container and not to
another PostgreSQL instance on Windows or WSL:

```powershell
docker logs --tail 80 postgres-server-octadim
docker exec postgres-server-octadim psql -U <POSTGRES_USER> -d <POSTGRES_DB_NAME> -c "SHOW hba_file; SHOW ssl; SELECT type,database,user_name,address,auth_method FROM pg_hba_file_rules ORDER BY line_number;"
```

For this local compose stack, `ssl` is expected to be `off`, and a normal
password connection should be handled by a `host ... scram-sha-256` rule. If
the DBeaver error does not appear in `docker logs`, DBeaver is reaching a
different PostgreSQL server. In that case, set the DBeaver host back to
`127.0.0.1`, verify the published port with `docker port postgres-server-octadim`,
and recreate the compose container if the host port is missing.

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
