# RabbitMQ aio-pika Runbook

## Files

- Local compose file: `local_docker-compose-rabbitmq_aiopika.yaml`
- Local environment file: `.env_local_rabbitmq_aiopika`
- IP-bound compose file: `ip_docker-compose-rabbitmq_aiopika.yaml`
- IP-bound environment file: `.env.ip_rabbitmq_aiopika`
- Host data directory: `RABBITMQ_DATA_DIR` from the selected environment file

## Local Start

```powershell
docker-compose -f local_docker-compose-rabbitmq_aiopika.yaml --env-file .env_local_rabbitmq_aiopika up -d
```

## Local Stop

```powershell
docker-compose -f local_docker-compose-rabbitmq_aiopika.yaml --env-file .env_local_rabbitmq_aiopika down
```

## IP-Bound Start

```powershell
docker-compose -f ip_docker-compose-rabbitmq_aiopika.yaml --env-file .env.ip_rabbitmq_aiopika up -d
```

## IP-Bound Stop

```powershell
docker-compose -f ip_docker-compose-rabbitmq_aiopika.yaml --env-file .env.ip_rabbitmq_aiopika down
```

## Validate Configuration

```powershell
docker-compose -f local_docker-compose-rabbitmq_aiopika.yaml --env-file .env_local_rabbitmq_aiopika config --quiet
docker-compose -f ip_docker-compose-rabbitmq_aiopika.yaml --env-file .env.ip_rabbitmq_aiopika config --quiet
```

## Access

- Local AMQP endpoint: `amqp://<RABBITMQ_DEFAULT_USER>:<RABBITMQ_DEFAULT_PASS>@127.0.0.1:<RABBITMQ_AMQP_PORT>/<RABBITMQ_DEFAULT_VHOST>`
- Local management UI: `http://127.0.0.1:<RABBITMQ_MANAGEMENT_PORT>`
- IP-bound AMQP endpoint: `amqp://<RABBITMQ_DEFAULT_USER>:<RABBITMQ_DEFAULT_PASS>@176.124.136.22:<RABBITMQ_AMQP_PORT>/<RABBITMQ_DEFAULT_VHOST>`
- IP-bound management UI: `http://176.124.136.22:<RABBITMQ_MANAGEMENT_PORT>`
- User: `RABBITMQ_DEFAULT_USER` from the selected environment file
- Password: `RABBITMQ_DEFAULT_PASS` from the selected environment file
- Virtual host: `RABBITMQ_DEFAULT_VHOST` from the selected environment file

For aio-pika clients, URL-encode the virtual host if it contains reserved URL
characters. The default value `octadim_aiopika` does not require encoding.

## Useful Commands

```powershell
docker-compose -f local_docker-compose-rabbitmq_aiopika.yaml --env-file .env_local_rabbitmq_aiopika ps
docker-compose -f local_docker-compose-rabbitmq_aiopika.yaml --env-file .env_local_rabbitmq_aiopika logs -f rabbitmq
docker-compose -f ip_docker-compose-rabbitmq_aiopika.yaml --env-file .env.ip_rabbitmq_aiopika ps
docker-compose -f ip_docker-compose-rabbitmq_aiopika.yaml --env-file .env.ip_rabbitmq_aiopika logs -f rabbitmq
docker exec -it local-rabbitmq-server-octadim-aiopika rabbitmq-diagnostics -q ping
docker exec -it ip-rabbitmq-server-octadim-aiopika rabbitmq-diagnostics -q ping
```

## Notes

- Run commands from the `docker_compose` directory.
- Use the local pair only for loopback access on `127.0.0.1`.
- Use the IP-bound pair only on a host that actually owns `176.124.136.22`; Docker cannot bind to an address missing from the host network interfaces.
- If startup fails with `Bind for 0.0.0.0:5672 failed: port is already allocated`,
  another host listener is already using AMQP. Check the rendered bind with
  `docker-compose -f local_docker-compose-rabbitmq_aiopika.yaml --env-file .env_local_rabbitmq_aiopika config`
  and inspect host listeners with `ss -ltnp | rg ':5672|:15672'`.
- Docker Desktop extensions or another RabbitMQ instance can publish
  `*:5672`/`*:15672` and block this stack even when this compose file renders
  `127.0.0.1:5672`/`127.0.0.1:15672`.
- RabbitMQ data is bind-mounted from `RABBITMQ_DATA_DIR`.
- `docker-compose down -v` does not delete files stored in `RABBITMQ_DATA_DIR`.
- Replace placeholder secrets in the selected `.env.*.rabbitmq_aiopika` file before real use.
