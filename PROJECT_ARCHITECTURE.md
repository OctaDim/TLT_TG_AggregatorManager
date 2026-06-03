Created by: Codex
Date: 2026-06-03

# Project Architecture

## Overview and Purpose

AI_TLT_TG_AggregatorManager is a Python service for managing Telegram clients
through Telethon and exposing operational workflows through a FastAPI HTTP API.
The service starts configured Telegram account and bot clients, processes
Telegram events, sends messages and files, supports web-driven authorization
flows, persists configuration and admin users in PostgreSQL, and stores or
retrieves media through S3-compatible object storage.

The application is built as a single runtime process started from `main.py`.
It combines:

- FastAPI routers grouped by business feature.
- Telethon client lifecycle and event handling.
- SQLAlchemy 2.x PostgreSQL persistence.
- SQLAdmin-based administrative UI.
- aiobotocore-based S3 access.
- Docker Compose files and runbooks for local PostgreSQL, MinIO, and RabbitMQ.

This repository currently has `PROJECT_ARCHITECTURE.md` as a workspace-local
architecture guide. Keep it updated together with any code, configuration,
infrastructure, or directory-structure changes so future AI-agent sessions do
not have to rediscover the same project map.

## Runtime Flow

1. `main.py` initializes PostgreSQL tables synchronously.
2. Telethon session directories are prepared.
3. `TelethonManagerSingleton` loads active Telethon configurations from
   PostgreSQL and starts account or bot clients.
4. Telethon event handlers are registered according to `TELETHON_OPTIONS`.
5. Uvicorn starts the FastAPI app with Starlette `SessionMiddleware`.
6. FastAPI lifespan startup creates default SQLAdmin users.
7. FastAPI routers expose Telegram, file, auth, status, and configuration
   operations.
8. Shutdown disconnects Telethon clients, cancels Telethon tasks, and disposes
   async and sync PostgreSQL connection pools.

## High-Level Directory Structure

```text
.
|-- main.py                         # Application entry point and runtime orchestration.
|-- requirements.txt                # Pinned Python runtime dependencies.
|-- PROJECT_ARCHITECTURE.md         # Architecture and AI-agent development guide.
|-- .configs_*.ini                  # Local runtime configuration files with secrets/settings.
|-- admin_panel/                    # SQLAdmin auth backend and custom templates.
|   |-- admin_views/                # SQLAdmin authentication role backend.
|   `-- custom_templates/sqladmin/  # Customized SQLAdmin Jinja templates.
|-- configs/                        # Environment loading, options, enums, labels, filters.
|-- db_postgres/                    # PostgreSQL models, connections, init, queries.
|   |-- postgres_conn/              # SQLAlchemy async/sync engine and session helpers.
|   |-- postgres_init/              # Declarative base, table initialization, default users.
|   |-- postgres_models/            # ORM models for Telethon configs and admin roles.
|   |-- postgres_queries/           # Domain-specific database queries.
|   `-- postgres_queries_utils/     # Reusable query builder/update helpers.
|-- docker_compose/                 # Local PostgreSQL, MinIO, and RabbitMQ compose stacks/runbooks.
|   |-- .env_local_postgres         # Localhost PostgreSQL variables for 127.0.0.1.
|   |-- .env.ip_postgres            # IP-bound PostgreSQL variables for a concrete host IP.
|   |-- .env_local_s3_minio         # Localhost MinIO variables for 127.0.0.1.
|   |-- .env.ip_s3_minio            # IP-bound MinIO variables for a concrete host IP.
|   |-- .env_local_rabbitmq_aiopika # Localhost RabbitMQ variables for 127.0.0.1.
|   |-- .env.ip_rabbitmq_aiopika    # IP-bound RabbitMQ variables for a concrete host IP.
|   |-- local_docker-compose_postgres.yaml # PostgreSQL 16 stack bound through local env.
|   |-- ip_docker-compose_postgres.yaml # PostgreSQL 16 stack bound through IP env.
|   |-- local_docker-compose_s3_minio.yaml # MinIO stack bound through local env.
|   |-- ip_docker-compose_s3_minio.yaml # MinIO stack bound through IP env.
|   |-- local_docker-compose-rabbitmq_aiopika.yaml # RabbitMQ stack bound through local env.
|   |-- ip_docker-compose-rabbitmq_aiopika.yaml # RabbitMQ stack bound through IP env.
|   `-- *_RUNBOOK.md                # Operational runbooks for compose validation and local access.
|-- _docs/                          # Operational notes and committed project documentation.
|   |-- tlt_sensitive_config_samples/ # Sanitized examples for secret-bearing config files.
|   `-- _docs_event_params_descr/   # Telegram event field documentation and source notes.
|-- _tests/                         # Tests organized by the package being tested.
|   |-- docker_compose/             # Static compose/runbook contract tests.
|   |-- sensitive_config/           # Secret-safe sample-file contract tests.
|   `-- db_postgres/postgres_tests/ # Script-style PostgreSQL query checks.
|-- fast_api/                       # Feature-based FastAPI routers, schemas, helpers.
|-- meta_classes/                   # Shared metaclasses, currently singleton support.
|-- s3_async_managers/              # aiobotocore client manager and context helper.
|-- telethon_manager/               # Telethon clients, auth drivers, handlers, attr chains.
|-- utils_common/                   # Cross-cutting helpers.
|-- utils_specific/                 # Project-specific Telegram and webhook helpers.
`-- _docs/                          # Operational notes and Telegram event documentation.
```

Development-local folders such as `.venv3145/`, `.idea/`, `.codex/`, and
`.agents/` are present in the workspace but are not part of the application
runtime architecture. Runtime data folders such as `TELETHON_SESSIONS/`,
`TEMP_MINIO_FILES/`, `TEMP_MINIO_LOCAL_FILES/`, and
`RABBITMQ_AIOPIKA_LOCAL_DATA/` may also exist locally; treat them as generated
operational state, not source structure. `.agents/` is still relevant for
AI-agent operating instructions and should be checked before substantial edits.
In the current snapshot `.agents/` exists but contains no files.

## Key Modules

### `main.py`

- Defines the list of FastAPI routers.
- Creates the FastAPI application.
- Adds SQLAdmin and Starlette session middleware.
- Starts Telethon clients before the FastAPI server.
- Owns process-level startup and shutdown behavior.

### `fast_api/`

Feature modules follow a consistent layout:

- `router_*.py` contains an `APIRouter` with a prefix based on
  `API_OPTIONS.API_BASE_URL_NAME`.
- `scheme_*.py` contains Pydantic request/response schemas.
- `helper_*.py` contains endpoint-specific business logic where needed.

Current API feature areas include health checks, Telethon task status, starting
and stopping clients, phone and QR-code authorization completion, Telegram user
search, message sending, file sending, file retrieval, S3 presigned URL access,
and activation/deactivation of message configurations.

The active API surface is the router list in `main.py`; folder presence alone
does not mean the endpoint is mounted. In the current snapshot the mounted
routers are:

- `app_tlt_api_health_check` - service health check endpoint.
- `app_tlt_clients_tasks_status` - Telethon client task status endpoint.
- `app_start_new_telethon_client` - start a new Telegram account or bot client.
- `app_find_telegram_users_data` - search Telegram user data by configured
  lookup inputs.
- `app_send_message` - send Telegram messages.
- `app_tlt_configs_by_web_acc` - return Telethon configs by web account.
- `app_complete_auth_phone` - complete web-driven phone authorization.
- `app_complete_auth_qrcode` - complete web-driven QR-code authorization.
- `app_get_qrcode_image_file` - return generated QR-code image files.
- `app_stop_tlt_clients` - stop selected Telethon clients.
- `app_stop_clear_tlt_clients` - stop and clear selected Telethon clients.
- `app_reconnect_authed_tlt_clients` - reconnect authorized clients.
- `app_messages_configs_by_web_acc` - return message configs by web account.
- `app_messages_configs_activate` - activate message configs.
- `app_messages_accounts_deactivate` - deactivate message configs/accounts.
- `app_send_files` - upload and send Telegram files.
- `app_get_file_by_message_id` - fetch message media by message identifiers.
- `app_get_file_from_tlt_server` - return a file already stored on the service.
- `app_get_file_s3_presigned_url` - create S3-compatible presigned access URLs.

`fast_api/app_auth` and `fast_api/app_web_account` exist in the repository but
are not mounted in `main.py` in the current snapshot.

### `telethon_manager/`

This package owns Telegram client behavior:

- `telethon_clients_manager.py` is the central lifecycle manager and uses
  `SingletonMeta` to keep one in-process manager instance.
- `telethon_auth_drivers.py` implements console, phone, QR-code, and mixed
  authorization drivers.
- `telethon_client_config.py` defines runtime configuration objects.
- `telethon_register_handlers.py` attaches event handlers to clients.
- `telethon_handlers/` contains event-specific handlers.
- `telethon_attrs_chains/` contains chain-style attribute extraction logic for
  Telegram event payloads.

### `db_postgres/`

PostgreSQL persistence is implemented with SQLAlchemy 2.x:

- `postgres_conn/pgs_connection.py` defines singleton async and sync engines.
- `postgres_conn/postgres_session.py` provides session wrappers.
- `postgres_init/` defines the declarative base and table initialization.
- `postgres_models/telethon_configs_model.py` stores Telethon account/bot
  configuration.
- `postgres_models/auth_role_model.py` stores SQLAdmin authentication roles.
- `postgres_queries/` contains domain-specific operations.
- `postgres_queries_utils/` contains generic filtering, ordering, update, and
  object conversion helpers.
- The sync SQLAlchemy engine uses the `postgresql+psycopg2` dialect, supplied
  in this local Python 3.14 environment by `psycopg2-binary`. Keep
  `psycopg2-binary` in `requirements.txt` unless system `pg_config`/`libpq-dev`
  is intentionally available for building source `psycopg2`.
- SQLAdmin default-user creation goes through
  `db_postgres/postgres_queries_utils/save_new_model_object.py`; pass
  `log_new_data=False` for seeded auth rows to avoid printing credentials.

### `admin_panel/`

The admin UI uses SQLAdmin with custom templates under
`admin_panel/custom_templates/sqladmin`. Authentication is handled by
`AdminAuthRoleAuthBackend`, which uses the `admin_auth_role` PostgreSQL table.
The admin base URL is configured as `/admin_panel`.

### `s3_async_managers/`

S3-compatible storage is accessed through aiobotocore. `AioBotoCoreManager`
creates and caches an async client configured from `.configs_s3_aws_api.ini`.
The code is compatible with MinIO because the endpoint URL is configurable.

### `configs/`

Configuration is centralized but mostly import-time:

- `.env` provides test API credentials.
- `.configs_api.ini` controls FastAPI host, port, credentials, and session key.
- `.configs_telegram.ini` controls Telegram API credentials.
- `.configs_proxy.ini` controls Telethon proxy settings.
- `.configs_sqladmin.ini` controls SQLAdmin seed users.
- `.configs_postgres.ini` controls PostgreSQL connection settings.
- `.configs_aggregator.ini` controls external aggregator API settings.
- `.configs_s3_aws_api.ini` controls S3/MinIO settings.

The selected config section depends on detected external IP and `sys.platform`.
This is important for agents: importing `configs.environments` may perform
network/IP checks and read local secret-bearing config files.

In the current local WSL workspace all selectable `.configs_*.ini` service
sections are intentionally loopback-oriented. API, PostgreSQL, aggregator,
S3/MinIO, and SOCKS proxy host values resolve to `127.0.0.1`; PostgreSQL uses
the Docker-published port `15432`, and S3/MinIO uses the Docker Compose
credentials and default bucket from `docker_compose/.env.s3_minio`.

### `_docs/tlt_sensitive_config_samples/`

This directory contains safe-to-commit examples for secret-bearing local
configuration. `root_configs/` mirrors the root `.configs_*.ini` files, and
`docker_compose/` mirrors the split Docker Compose env files. The sample files
preserve the same sections and parameter names as the real files. Values are
fake but realistic enough to show the expected format for hosts, ports, user
names, passwords, keys, hashes, bucket names, and data paths.

Update these examples whenever real config files gain, remove, or rename
parameters. Real `.configs_*.ini`, `docker_compose/.env.*`, and
`docker_compose/.env_local_*` files remain ignored and must not be committed.

## AI-Agent Development Map

This section is intentionally practical. Use it when making changes so the next
agent can quickly find the correct registration point and verification path.

### Adding or Changing a FastAPI Endpoint

1. Create or update a feature folder under `fast_api/app_*`.
2. Put request/response models in `scheme_*.py`.
3. Put the `APIRouter` in `router_*.py`.
4. Put endpoint-specific operational logic in `helper_*.py` when the router
   would otherwise become orchestration-heavy.
5. Register the router in `main.py` by importing it and adding it to
   `routers_list`.
6. Keep the route prefix aligned with `API_OPTIONS.API_BASE_URL_NAME` unless
   intentionally creating a separate public surface.
7. Update this architecture file with the new feature area and any new external
   dependencies.

### Adding or Changing a PostgreSQL Model

1. Add or update the SQLAlchemy model under `db_postgres/postgres_models/`.
2. Import the model in `db_postgres/postgres_init/db_tables_init_imports.py`.
   This import file is required because table creation uses `Base.metadata` and
   only models imported before initialization are registered.
3. Add domain query functions under `db_postgres/postgres_queries/`.
4. Reuse generic helpers from `db_postgres/postgres_queries_utils/` for filters,
   ordering, object creation, and updates.
5. Use `PgsAsyncSession` for runtime async flows and `PgsSyncConnection` only
   for synchronous initialization-style operations.
6. Verify against a real configured PostgreSQL instance before claiming data
   migrations or runtime persistence are working.

### Adding or Changing Telethon Event Handling

1. Register new Telethon event handlers in
   `telethon_manager/telethon_register_handlers.py`.
2. Put event-specific logic in `telethon_manager/telethon_handlers/`.
3. Put reusable event attribute extraction in
   `telethon_manager/telethon_attrs_chains/`.
4. Check `TELETHON_OPTIONS` before assuming an event should be handled or logged.
5. Keep webhook payloads JSON-safe by passing values through
   `utils_common.serialize_custom_json.get_only_jsonable_values`.
6. If event data is sent outside the service, follow the existing path through
   `utils_specific/handle_all_event_params.py` and
   `utils_specific/send_event_data_webhook.py`.

### Adding or Changing S3/File Behavior

1. Keep async S3 client creation in `s3_async_managers/`.
2. Use `.configs_s3_aws_api.ini` values through `configs.environments` rather
   than duplicating endpoint or credential parsing.
3. Keep temporary Telethon downloads aligned with `TELETHON_OPTIONS` directory
   settings.
4. Preserve timeout behavior for uploads, downloads, and presigned URLs unless
   changing the user-facing contract intentionally.

### Adding or Changing Admin Panel Behavior

1. Keep SQLAdmin authentication logic under `admin_panel/admin_views/`.
2. Keep template overrides under `admin_panel/custom_templates/sqladmin/`.
3. Register any SQLAdmin model views through `admin_panel_views` in `main.py`.
   It is currently empty, so adding model views requires explicit registration.
4. Keep auth role persistence aligned with `AuthRoleModel`.

## Data and Responsibility Boundaries

- FastAPI routers should validate and orchestrate; Telethon manager methods
  should own Telegram client state transitions.
- Telethon handlers should extract and normalize event data; external delivery
  belongs in `utils_specific/send_event_data_webhook.py`.
- PostgreSQL query modules should own persistence details; API helpers should
  call query functions rather than constructing ORM statements inline.
- S3 manager modules should own S3 client lifecycle; feature helpers should call
  them instead of creating aiobotocore clients directly.
- `configs/options.py` is the right place for feature flags and operational
  constants; `.configs_*.ini` files are for environment-specific values and
  secrets.

## Runtime Side Effects to Remember

- Importing `configs.environments` can read local config files and perform IP
  detection immediately.
- Starting `main.py` can create database tables, create default SQLAdmin users,
  start Telethon clients, and open network connections.
- `PgsAsyncSession` and `PgsSyncSession` commit automatically when leaving a
  successful context manager block and roll back on errors.
- `TelethonManagerSingleton` stores mutable process-wide dictionaries for
  clients, configs, handlers, QR-code logins, and running tasks.
- Some file and media helpers create temporary or archive files according to
  `TELETHON_OPTIONS`.

## Technology Stack

- Python 3.14 local virtual environment is present in `.venv3145/`.
- FastAPI 0.128.1, Starlette 0.50.0, Uvicorn 0.40.0.
- Pydantic 2.12.5.
- Telethon 1.42.0.
- SQLAlchemy 2.0.46 with asyncpg and psycopg2-binary drivers.
- SQLAdmin 0.23.0 with Jinja2 templates and Starlette sessions.
- PostgreSQL 16 Alpine for the local/IP compose stacks.
- aiobotocore 3.7.0 and botocore 1.43.0 for S3-compatible storage.
- MinIO compose stacks for local and IP-bound S3-compatible storage.
- RabbitMQ 3.13 management image for local and IP-bound aio-pika-oriented
  compose stacks.
- qrcode, Pillow, hachoir, aiofiles, aioshutil, requests, httpx, and utility
  libraries for media, file, and HTTP workflows.

## External Services and Infrastructure

### PostgreSQL

- Local compose file: `docker_compose/local_docker-compose_postgres.yaml`.
- Local env file: `docker_compose/.env_local_postgres`.
- IP-bound compose file: `docker_compose/ip_docker-compose_postgres.yaml`.
- IP-bound env file: `docker_compose/.env.ip_postgres`.
- Runbook: `docker_compose/POSTGRES_RUNBOOK.md`.
- Compose project names: `octadim_local_postgres` and `octadim_ip_postgres`.
- The Python app reads PostgreSQL runtime settings from `.configs_postgres.ini`.
- The compose stack reads infrastructure settings from
  the selected `.env.*.postgres` file.
- The local Windows/WSL PostgreSQL config sections in `.configs_postgres.ini`
  should stay aligned with the chosen PostgreSQL compose env file; in this
  workspace the Docker-published local port is `15432` to avoid conflicts with
  native Windows or Ubuntu PostgreSQL services on `5432`.
- All PostgreSQL config sections currently point to the local compose database
  `wsl_octadim_dexp` on `127.0.0.1:15432` so the external-IP section selector
  cannot accidentally route the service to a remote database.
- Compose env files are local environment data. Treat them as secret-bearing
  files and avoid printing or committing real credentials.
- PostgreSQL's container log may report `listening on IPv4 address "0.0.0.0"`
  and `listening on IPv6 address "::"` because the official PostgreSQL image
  starts the server inside the container with broad internal listen addresses.
  Host exposure is still controlled separately by the Compose `ports` mapping,
  which publishes container port `5432` on the host address selected by the
  env file.
- Windows DBeaver access to the WSL-hosted PostgreSQL compose stack is
  documented in `docker_compose/POSTGRES_RUNBOOK.md`. The default connection
  path is `127.0.0.1:${POSTGRES_PORT:-5432}` through Docker/WSL localhost
  forwarding. In WSL2 mirrored networking mode, use a non-default host port
  such as `15432` for this compose stack when Windows or Ubuntu already has
  PostgreSQL on `5432`. If a previously created container is healthy but has no
  published host port, recreate it with the current compose file so the port
  mapping is applied.
- DBeaver `no pg_hba.conf entry ... no encryption` errors should be diagnosed
  by checking `docker logs postgres-server-octadim` and active
  `pg_hba_file_rules` first. In this local stack SSL is normally off, so that
  error often means DBeaver reached another PostgreSQL instance or an old
  container instead of the compose service documented here.

### S3 / MinIO

- Local compose file: `docker_compose/local_docker-compose_s3_minio.yaml`.
- Local env file: `docker_compose/.env_local_s3_minio`.
- IP-bound compose file: `docker_compose/ip_docker-compose_s3_minio.yaml`.
- IP-bound env file: `docker_compose/.env.ip_s3_minio`.
- Runbook: `docker_compose/S3_MINIO_RUNBOOK.md`.
- Compose project names: `octadim_local_s3_minio` and `octadim_ip_s3_minio`.
- The Python app reads S3 runtime settings from `.configs_s3_aws_api.ini`.
- The compose stack reads infrastructure settings from
  the selected `.env.*.s3_minio` file.
- Compose env files are local environment data. Treat them as secret-bearing
  files and avoid printing or committing real credentials.
- All S3 config sections currently point to local MinIO at `127.0.0.1:9000`,
  using the access key, secret key, and default bucket from the local compose
  env file. The local bucket name uses hyphens (`minio-bucket-1`) because S3
  bucket names cannot contain underscores.

### RabbitMQ / aio-pika

- Local compose file:
  `docker_compose/local_docker-compose-rabbitmq_aiopika.yaml`.
- Local env file: `docker_compose/.env_local_rabbitmq_aiopika`.
- IP-bound compose file:
  `docker_compose/ip_docker-compose-rabbitmq_aiopika.yaml`.
- IP-bound env file: `docker_compose/.env.ip_rabbitmq_aiopika`.
- Runbook: `docker_compose/RABBITMQ_AIOPIKA_RUNBOOK.md`.
- Compose project names: `octadim_local_rabbitmq_aiopika` and
  `octadim_ip_rabbitmq_aiopika`.
- The compose stack reads infrastructure settings from
  the selected `.env.*.rabbitmq_aiopika` file.
- The stack publishes AMQP on
  `${RABBITMQ_EXTERNAL_IP:-127.0.0.1}:${RABBITMQ_AMQP_PORT:-5672}` and the
  management UI on
  `${RABBITMQ_EXTERNAL_IP:-127.0.0.1}:${RABBITMQ_MANAGEMENT_PORT:-15672}`.
- If RabbitMQ startup fails with `Bind for 0.0.0.0:5672 failed: port is
  already allocated`, render the selected compose file with `docker compose
  config` and inspect host listeners with `ss -ltnp | rg ':5672|:15672'`.
  A listener on `*:5672` or `*:15672` can block this stack even when the
  rendered compose file asks Docker to bind `127.0.0.1`.
- Persistent broker state is bind-mounted from `RABBITMQ_DATA_DIR` after a
  one-shot init container verifies that the host directory exists and is
  writable.
- The healthcheck uses `rabbitmq-diagnostics -q ping` inside the broker
  container. This is a broker readiness signal, not proof that any application
  queue topology has been declared.
- Compose env files are local environment data. Treat them as secret-bearing
  files and avoid printing or committing real credentials.
- RabbitMQ is currently an infrastructure option for future aio-pika based
  messaging. No active Python RabbitMQ client or queue-processing code is wired
  into `main.py` in the current snapshot.

### External Aggregator API

Telegram event data can be normalized and sent to an external aggregator through
helpers in `utils_specific/`. Aggregator credentials and host settings are read
from `.configs_aggregator.ini`.

## Key Architectural Patterns

- Feature folder pattern for FastAPI modules: router, schema, and helper files
  live together under `fast_api/app_*`.
- Singleton pattern for long-lived resources such as Telethon manager and
  PostgreSQL engines.
- Repository/query-helper style for database access: domain queries call shared
  query utility builders instead of embedding all SQL in routers.
- Chain-of-responsibility style attribute extraction for Telethon events and
  downloaded file metadata.
- Async-first runtime for Telegram clients, FastAPI handlers, PostgreSQL access,
  and S3 access.
- Import-time configuration selection based on machine/network context.
- Script-style operational tests currently coexist with standard unittest tests.

## Architecture Decision Records

### ADR-001: FastAPI for the HTTP API

FastAPI is used because the service needs async endpoints, Pydantic validation,
automatic OpenAPI support during development, and straightforward integration
with Uvicorn and Starlette middleware. This fits the Telethon async runtime
better than a synchronous framework.

### ADR-002: Telethon for Telegram Client Management

Telethon is used because the application manages both Telegram user accounts and
bots, needs session strings/files, QR-code and phone auth flows, event handlers,
and direct Telegram API access. Bot-only libraries would not cover account-based
workflows.

### ADR-003: PostgreSQL Instead of SQLite for Runtime State

PostgreSQL is used for durable service state such as Telethon configurations and
admin roles. SQLAlchemy async and sync engines are both present because the
application combines async runtime operations with synchronous table
initialization. SQLite remains relevant only indirectly through Telethon session
implementation details.

### ADR-004: SQLAdmin for Administrative UI

SQLAdmin is used to provide an admin interface on top of SQLAlchemy models with
minimal custom UI code. Custom templates are kept under `admin_panel/` so local
layout/auth changes can be made without replacing the admin framework.

### ADR-005: S3-Compatible Storage Through aiobotocore

aiobotocore is used to keep storage operations async and compatible with both
AWS S3 and MinIO. MinIO is documented as the local compose target, while the app
retains configurable endpoint, service, region, and credentials.

### ADR-006: Redis Is Not an Active Runtime Dependency Yet

`main.py` contains TODO placeholders for Redis availability checks, and server
docs mention Redis service preparation. There is no active Redis client or
runtime dependency in `requirements.txt`; agents should treat Redis as planned
or historical documentation unless code is added.

### ADR-007: Local INI Files for Environment-Specific Configuration

The project uses multiple `.configs_*.ini` files and IP/platform-based section
selection instead of one environment-only configuration layer. This preserves
the existing deployment style, but agents must avoid committing secrets and
should be careful when importing modules that load these files at import time.

### ADR-008: `main.py` as the Router and Runtime Composition Root

`main.py` remains the explicit composition root for mounted FastAPI routers,
SQLAdmin setup, Telethon startup, database initialization, and shutdown cleanup.
This keeps service wiring visible in one place, which is useful for a small
single-process service where implicit auto-discovery would hide startup order
and side effects. When adding API modules, update `main.py` deliberately and
document the new mounted surface here.

### ADR-009: Local Infrastructure Host Binding Stays Explicit

The local compose stacks use dedicated `local_` compose files and
`.env_local_*` files to bind published service ports to `127.0.0.1`. This lets
local tools and the Python application connect without exposing PostgreSQL,
MinIO, or RabbitMQ on all host interfaces. Container-internal services may
still listen broadly inside Docker; agents should distinguish internal listen
addresses from Docker's external host port publication when reviewing exposure
risk.

### ADR-010: RabbitMQ Compose Stack for aio-pika Integration Work

RabbitMQ is added as a local compose stack because aio-pika targets AMQP and
RabbitMQ provides a widely used AMQP broker with durable queues, virtual hosts,
and a management UI for inspecting local message flow. The stack is documented
as infrastructure only until Python code adds an aio-pika dependency and
explicit producer or consumer wiring. Redis remains separate because it is not
an AMQP broker and would change the messaging contract.

### ADR-011: Separate Compose and Env Files for Localhost and Concrete Host IP

Each compose-backed service has a `local_` compose file plus `.env_local_*`
file for loopback startup and an `ip_` compose file plus `.env.ip_*` file for a
specific host address such as `176.124.136.22`. The split keeps secrets and
published host bindings environment-specific without editing compose YAML. It
also prevents ambiguous run commands where a developer might accidentally start
a public-facing service with localhost credentials or vice versa.

### ADR-012: Sanitized Secret File Examples Are Committed Separately

The repository commits sanitized sample files under
`_docs/tlt_sensitive_config_samples/` instead of committing real local config
files.
This keeps future setup reproducible because agents and developers can see the
required sections and parameter names, while Git history stays free of real API
keys, passwords, session signing keys, Telegram credentials, proxy credentials,
and host-specific deployment secrets.

## Development Conventions

- Keep `PROJECT_ARCHITECTURE.md` synchronized with code, file structure, and
  infrastructure changes.
- The first two lines of this file must remain `Created by:` and `Date:`.
- Code comments and inline notes must be in English.
- Prefer existing feature-folder patterns when adding API modules.
- Prefer existing query helpers and SQLAlchemy models over ad hoc SQL.
- Keep secret-bearing `.configs_*.ini` files out of documentation examples and
  avoid printing full credentials in logs.
- Keep compose `.env.*` files local and secret-aware; runbooks may name them,
  but architecture docs should describe their purpose rather than include their
  contents.
- Keep compose `.env_local_*` files local and secret-aware too; `.gitignore`
  excludes both `.env.*` and `.env_local_*` patterns.
- Keep `_docs/tlt_sensitive_config_samples/` synchronized with real
  secret-bearing config file shapes. Samples must use fake but realistic values
  that show the expected format without copying real secrets.
- Keep runtime data directories such as `TEMP_MINIO_LOCAL_FILES/` and
  `RABBITMQ_AIOPIKA_LOCAL_DATA/` ignored and out of commits.
- Active `docker_compose/*docker-compose*.yaml` files must start with either
  `local_` or `ip_`. Match each compose file to its corresponding
  `.env_local_*` or `.env.ip_*` file.
- When adding a new FastAPI endpoint, add a router module, schema module, helper
  module if needed, and register the router in `main.py`.
- When adding persistent data, define or update an ORM model, include it in
  table initialization imports, add query helpers, and update this document.
- When adding a new external service, document config files, runbooks, compose
  files, lifecycle behavior, and the reason for the service.
- Do not assume Docker is available in every development environment; compose
  tests currently rely on static file validation.
- Prefer the repository-local `.venv3145/bin/python` for verification in this
  checkout; the plain `python` command may not be available when pyenv is set to
  `system`.

## Testing and Verification

Current automated verification is limited:

- `_tests/docker_compose/test_compose_configs.py` uses `unittest` to statically
  verify expected PostgreSQL, MinIO, and RabbitMQ compose contracts and runbook
  commands.
- `_tests/sensitive_config/test_sensitive_config_samples.py` compares committed
  sanitized samples with the ignored local config files so parameter drift is
  detected without committing secrets.
- `_tests/db_postgres/postgres_tests/` contains script-style database checks
  that require live PostgreSQL and project-specific model availability.
- The repository follows the convention that tests live under `_tests/` with a
  subdirectory corresponding to the package or infrastructure area being
  tested, for example `_tests/docker_compose/` and `_tests/db_postgres/`.
- Runtime startup verification still requires a configured PostgreSQL instance,
  Telegram credentials/sessions, S3-compatible storage, and any optional
  RabbitMQ messaging code that may be added later. Documentation-only checks
  should not be presented as proof that the full service starts.

Recommended checks after documentation-only edits:

- `.venv3145/bin/python -m py_compile main.py`
- `.venv3145/bin/python -m unittest _tests/docker_compose/test_compose_configs.py`
- `.venv3145/bin/python -m unittest _tests/sensitive_config/test_sensitive_config_samples.py`

Recommended checks after runtime code changes:

- Run relevant FastAPI/Telethon flow manually against a configured local
  environment.
- Run PostgreSQL query checks only when the expected database and config files
  are available.
- Validate compose files with Docker on a host where Docker is installed:
  `docker compose -f docker_compose/local_docker-compose_postgres.yaml --env-file docker_compose/.env_local_postgres config --quiet`
  and
  `docker compose -f docker_compose/ip_docker-compose_postgres.yaml --env-file docker_compose/.env.ip_postgres config --quiet`
  and
  `docker compose -f docker_compose/local_docker-compose_s3_minio.yaml --env-file docker_compose/.env_local_s3_minio config --quiet`
  and
  `docker compose -f docker_compose/ip_docker-compose_s3_minio.yaml --env-file docker_compose/.env.ip_s3_minio config --quiet`
  and
  `docker compose -f docker_compose/local_docker-compose-rabbitmq_aiopika.yaml --env-file docker_compose/.env_local_rabbitmq_aiopika config --quiet`
  and
  `docker compose -f docker_compose/ip_docker-compose-rabbitmq_aiopika.yaml --env-file docker_compose/.env.ip_rabbitmq_aiopika config --quiet`.

## Known Risks and Agent Notes

- `PROJECT_ARCHITECTURE.md` is tracked in Git in the current checkout and must
  be kept synchronized with source, infrastructure, and documentation changes.
- Split compose env files under `docker_compose/.env_local_*` and
  `docker_compose/.env.ip_*` are local secret-bearing files. Older unsplit
  `.env.postgres`, `.env.s3_minio`, and `.env.rabbitmq_aiopika` files may still
  exist in a developer workspace as legacy local data, but runbooks should use
  the split files. `.gitignore` excludes both split env naming patterns.
- The committed config examples under `_docs/tlt_sensitive_config_samples/` are
  intentionally sanitized even though they use realistic-looking values. Never
  copy real secret values into these examples.
- Plain `python` and direct `python3.14` commands may fail under the current
  pyenv setup; `.venv3145/bin/python` is the verified local interpreter.
- Importing `configs.environments` can run IP detection and read local config
  files; avoid importing it in tests unless that behavior is intended.
- The application uses singleton instances for core runtime resources, so tests
  may need explicit cleanup between runs.
- Some TODOs describe future background tasks, Redis checks, handler lifecycle
  improvements, and QR-code image handling.
- `_tests/db_postgres/postgres_tests/test_get_model_records_flex_qry.py`
  references a `postgres_models.__temp` import path that is not present in the
  current file listing; treat it as an experimental script until updated.
- `admin_panel_views` is currently empty in `main.py`, so SQLAdmin is mounted
  but no model views are registered there by default.

## Detailed Documentation Links

- `docker_compose/POSTGRES_RUNBOOK.md` - PostgreSQL compose usage, validation,
  and Windows DBeaver connection guidance for WSL-hosted containers.
- `docker_compose/S3_MINIO_RUNBOOK.md` - MinIO compose usage and validation.
- `_docs/_docs_server_linux/` - Linux service deployment notes.
- `_docs/_docs_event_params_descr/` - Telegram event parameter documentation.
- `_tests/docker_compose/test_compose_configs.py` - static tests for compose
  contracts.
