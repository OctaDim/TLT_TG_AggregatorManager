# sshpass Tools Runbook

## Files

- Local compose file: `local_docker-compose_sshpass.yaml`
- IP-mode compose file: `ip_docker-compose_sshpass.yaml`

## Local Start

```powershell
docker-compose -f local_docker-compose_sshpass.yaml up -d
```

## Local Stop

```powershell
docker-compose -f local_docker-compose_sshpass.yaml down
```

## IP-Mode Start

```powershell
docker-compose -f ip_docker-compose_sshpass.yaml up -d
```

## IP-Mode Stop

```powershell
docker-compose -f ip_docker-compose_sshpass.yaml down
```

## Validate Configuration

```powershell
docker-compose -f local_docker-compose_sshpass.yaml config --quiet
docker-compose -f ip_docker-compose_sshpass.yaml config --quiet
```

## Access

```powershell
docker exec local-sshpass-tools-octadim sshpass -V
docker exec local-sshpass-tools-octadim ssh -V
docker exec ip-sshpass-tools-octadim sshpass -V
docker exec ip-sshpass-tools-octadim ssh -V
```

## Notes

- Run commands from the `docker_compose` directory.
- The IP-mode file exists to mirror the repository's `local_` / `ip_` compose
  split. This helper does not publish inbound ports.
- The helper container installs `openssh-client` and `sshpass` from Alpine
  packages at container startup, verifies both tools, and then stays alive for
  `docker exec` usage.
- The helper stack does not store passwords or SSH targets in Compose files.
  Pass sensitive values at execution time through your normal secret-handling
  workflow.
- Use `sshpass` only for development or operational cases where key-based SSH
  is not available. Prefer SSH keys for durable automation.
