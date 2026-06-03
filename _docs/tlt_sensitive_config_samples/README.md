# Sensitive Configuration Samples

This directory documents local secret-bearing configuration files without
storing real secrets in Git.

## Purpose

Real runtime configuration files such as `.configs_*.ini` and
`docker_compose/.env*` are intentionally ignored by Git because they can contain
API credentials, Telegram API credentials, PostgreSQL passwords, MinIO keys,
RabbitMQ passwords, session keys, proxy credentials, and deployment-specific
host data.

The files in this directory are committed examples. They preserve the same file
shape, section names, and parameter names as the real local files. Values are
fake but realistic, so developers can see the expected format for hosts, ports,
usernames, passwords, access keys, hashes, bucket names, and data paths without
exposing real secrets.

## Layout

- `root_configs/` contains examples for root-level `.configs_*.ini` files.
- `docker_compose/` contains examples for Docker Compose environment files.

## Root Config Files

- `.configs_aggregator.ini.example` - external aggregator API host, port, and
  basic authentication values.
- `.configs_api.ini.example` - FastAPI host, port, API credentials, and session
  signing key.
- `.configs_postgres.ini.example` - application PostgreSQL connection values.
- `.configs_proxy.ini.example` - Telethon proxy type, address, port, DNS, and
  optional proxy credentials.
- `.configs_s3_aws_api.ini.example` - S3-compatible endpoint, access key,
  secret key, bucket, service name, and region.
- `.configs_sqladmin.ini.example` - seeded SQLAdmin user credentials.
- `.configs_telegram.ini.example` - Telegram official API ID and hash values.

## Docker Compose Env Files

- `.env_local_postgres.example` - localhost PostgreSQL compose variables.
- `.env.ip_postgres.example` - concrete-host-IP PostgreSQL compose variables.
- `.env_local_s3_minio.example` - localhost MinIO compose variables.
- `.env.ip_s3_minio.example` - concrete-host-IP MinIO compose variables.
- `.env_local_rabbitmq_aiopika.example` - localhost RabbitMQ compose
  variables.
- `.env.ip_rabbitmq_aiopika.example` - concrete-host-IP RabbitMQ compose
  variables.

## Update Rules

When a real secret-bearing config file gains, removes, or renames a parameter,
update the matching sample file in the same change. Keep example values
realistic enough to show the expected format, but never copy real credentials,
tokens, API hashes, passwords, cookies, or host-specific secret values into this
directory.

Run this contract check after updating samples:

```bash
.venv3145/bin/python -m unittest _tests/sensitive_config/test_sensitive_config_samples.py
```
