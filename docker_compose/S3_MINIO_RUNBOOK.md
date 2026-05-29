# S3 MinIO Runbook

## Files

- Compose file: `docker-compose_s3_minio.yaml`
- Environment file: `.env.s3_minio`
- Host data directory: `MINIO_DATA_DIR` from `.env.s3_minio`

## Start

```powershell
docker-compose -f docker-compose_s3_minio.yaml --env-file .env.s3_minio up -d
```

## Stop

```powershell
docker-compose -f docker-compose_s3_minio.yaml --env-file .env.s3_minio down
```

## Validate Configuration

```powershell
docker-compose -f docker-compose_s3_minio.yaml --env-file .env.s3_minio config --quiet
```

## Useful Commands

```powershell
docker-compose -f docker-compose_s3_minio.yaml --env-file .env.s3_minio ps
docker-compose -f docker-compose_s3_minio.yaml --env-file .env.s3_minio logs -f minio
docker-compose -f docker-compose_s3_minio.yaml --env-file .env.s3_minio logs create-minio-buckets
docker inspect minio-server-octadim
docker exec -it minio-server-octadim mc ready local
docker exec -it minio-server-octadim mc alias set local http://127.0.0.1:9000 <MINIO_ROOT_USER> <MINIO_ROOT_PASSWORD>
docker exec -it minio-server-octadim mc ls local
```

## Access

- S3 API: `http://<MINIO_EXTERNAL_IP>:<MINIO_API_PORT>`
- Web console: `http://<MINIO_EXTERNAL_IP>:<MINIO_CONSOLE_PORT>`
- Root user: `MINIO_ROOT_USER` from `.env.s3_minio`
- Root password: `MINIO_ROOT_PASSWORD` from `.env.s3_minio`

## Notes

- Run commands from the `docker_compose` directory.
- Use `--env-file .env.s3_minio`; the shared `.env` file is deprecated.
- MinIO data is bind-mounted from `MINIO_DATA_DIR`.
- `MINIO_DEFAULT_BUCKETS` is a space-separated list of buckets created by `create-minio-buckets`.
