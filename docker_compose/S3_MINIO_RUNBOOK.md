# S3 MinIO Runbook

## Files

- Local compose file: `local_docker-compose_s3_minio.yaml`
- Local environment file: `.env_local_s3_minio`
- IP-bound compose file: `ip_docker-compose_s3_minio.yaml`
- IP-bound environment file: `.env.ip_s3_minio`
- Host data directory: `MINIO_DATA_DIR` from the selected environment file

## Local Start

```powershell
docker-compose -f local_docker-compose_s3_minio.yaml --env-file .env_local_s3_minio up -d
```

## Local Stop

```powershell
docker-compose -f local_docker-compose_s3_minio.yaml --env-file .env_local_s3_minio down
```

## IP-Bound Start

```powershell
docker-compose -f ip_docker-compose_s3_minio.yaml --env-file .env.ip_s3_minio up -d
```

## IP-Bound Stop

```powershell
docker-compose -f ip_docker-compose_s3_minio.yaml --env-file .env.ip_s3_minio down
```

## Validate Configuration

```powershell
docker-compose -f local_docker-compose_s3_minio.yaml --env-file .env_local_s3_minio config --quiet
docker-compose -f ip_docker-compose_s3_minio.yaml --env-file .env.ip_s3_minio config --quiet
```

## Access

- Local S3 API: `http://127.0.0.1:<MINIO_API_PORT>`
- Local web console: `http://127.0.0.1:<MINIO_CONSOLE_PORT>`
- IP-bound S3 API: `http://176.124.136.22:<MINIO_API_PORT>`
- IP-bound web console: `http://176.124.136.22:<MINIO_CONSOLE_PORT>`
- Root user: `MINIO_ROOT_USER` from the selected environment file
- Root password: `MINIO_ROOT_PASSWORD` from the selected environment file

## Useful Commands

```powershell
docker-compose -f local_docker-compose_s3_minio.yaml --env-file .env_local_s3_minio ps
docker-compose -f local_docker-compose_s3_minio.yaml --env-file .env_local_s3_minio logs -f minio
docker-compose -f ip_docker-compose_s3_minio.yaml --env-file .env.ip_s3_minio ps
docker-compose -f ip_docker-compose_s3_minio.yaml --env-file .env.ip_s3_minio logs -f minio
docker exec -it local-minio-server-octadim mc ready local
docker exec -it ip-minio-server-octadim mc ready local
```

## Notes

- Run commands from the `docker_compose` directory.
- Use the local pair only for loopback access on `127.0.0.1`.
- Use the IP-bound pair only on a host that actually owns `176.124.136.22`; Docker cannot bind to an address missing from the host network interfaces.
- MinIO data is bind-mounted from `MINIO_DATA_DIR`.
- `MINIO_DEFAULT_BUCKETS` is a space-separated list of buckets created by `create-minio-buckets`.
- Replace placeholder secrets in the selected `.env.*.s3_minio` file before real use.
