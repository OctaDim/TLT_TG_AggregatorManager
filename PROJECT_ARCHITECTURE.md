Created by: Codex
Date: 2026-06-29
Time: 10:18:42 UTC

# Project Architecture

## Purpose

TLT TG Aggregator Manager is a Python service that runs multiple Telegram clients through Telethon, exposes management and messaging operations through FastAPI, stores Telegram client configuration in PostgreSQL, and forwards Telegram event data to an external aggregator API. The service also supports local/S3-compatible file storage for Telegram media and provides a SQLAdmin-based administration surface.

## Current Runtime Shape

The application is started from `main.py`.

1. PostgreSQL tables are initialized synchronously before the asyncio runtime starts.
2. Telethon session directories are prepared.
3. Telethon client configurations are loaded from PostgreSQL.
4. Telethon clients are created, authenticated, registered with event handlers, and run as background asyncio tasks.
5. A FastAPI application is created in the same process and served by Uvicorn as another asyncio task.
6. On shutdown, Telethon clients are disconnected, running Telethon tasks are cancelled, and async/sync PostgreSQL engines are disposed.

The process is therefore a single asyncio application that combines:

- Long-running Telethon client tasks.
- FastAPI request/response API.
- SQLAdmin UI mounted on the FastAPI app.
- PostgreSQL persistence.
- Optional S3-compatible media storage.
- Outbound webhook calls to an external aggregator API.

## Directory Structure

```text
.
|-- main.py
|   Application entry point. Initializes database tables, starts Telethon clients,
|   builds FastAPI, mounts SQLAdmin, and coordinates shutdown cleanup.
|-- requirements.txt
|   Pinned Python dependencies.
|-- PROJECT_ARCHITECTURE.md
|   Architecture guide for humans and AI agents.
|-- configs/
|   Configuration constants, environment/config-file readers, enums, labels,
|   options, and external API URL builders.
|-- fast_api/
|   FastAPI routers, request schemas, and endpoint helpers. Each app_* package
|   owns one functional API area.
|-- telethon_manager/
|   Telethon client lifecycle, authentication drivers, event handler registration,
|   event attribute chains, QR login state, and client config contracts.
|-- db_postgres/
|   SQLAlchemy engines/sessions, ORM models, table initialization, query helpers,
|   application queries, and existing PostgreSQL-oriented tests.
|-- admin_panel/
|   SQLAdmin authentication backend and custom SQLAdmin templates.
|-- s3_async_managers/
|   aiobotocore-based S3-compatible client helpers.
|-- utils_common/
|   Reusable generic utilities for files, paths, validation, JSON serialization,
|   password hashing, QR code image creation, text cleanup, and timing.
|-- utils_specific/
|   Project-specific utilities for Telethon event serialization, webhook sending,
|   proxy config conversion, and selecting usable Telegram clients.
|-- docker_compose/
|   Docker Compose definition for MinIO/S3-compatible local storage. Contains a
|   local `.env` file; do not document or commit its secret values.
|-- _docs/
|   Operational and Telethon event reference documentation.
|-- _docs/_docs_server_linux/
|   Linux service examples and startup notes.
|-- _docs/_docs_event_params_descr/
|   Telegram/Telethon event parameter notes.
|-- TELETHON_SESSIONS/
|   Local Telethon session files. Sensitive runtime state; do not inspect,
|   document, or commit contents.
|-- TEMP_TELETHON_TEMP_FILES/
|   Temporary downloaded Telegram media files.
|-- TEMP_TELETHON_ARCHIVE_FILES/
|   Archive directory for downloaded Telegram media.
|-- TEMP_QRCODE_IMAGES/
|   Generated QR-code images used by QR authentication flows.
|-- zExamples/
|   Ignored example/experimental files.
|-- zProxyBackup/
|   Proxy config backups. Treat as sensitive.
```

The directories `zBackUp/` and `zTest/` must always be skipped during analysis, per repository instructions.

## Key Modules

### `main.py`

- Defines the FastAPI router list.
- Creates the FastAPI app and wraps it with Starlette `SessionMiddleware`.
- Sets up SQLAdmin with `AdminAuthRoleAuthBackend`.
- Starts Telethon before the HTTP server.
- Runs Uvicorn via `uvicorn.Server` as an asyncio task when combined with Telethon.
- Handles graceful shutdown for Telethon clients, Telethon tasks, and PostgreSQL connections.

### `configs/`

- `environments.py` reads `.env` and multiple `.configs_*.ini` files through `ConfigParser`.
- Runtime config section selection is based on detected external IP and platform.
- `options.py` centralizes behavioral switches for FastAPI, SQLAlchemy, SQLAdmin, Telethon, S3/media, user search, messaging, and external aggregator calls.
- `enums.py` defines domain enums such as user roles, Telegram account types, and QR error correction levels.
- `aggregator_api_urls.py` builds external aggregator URLs from configured host/port values.

Sensitive values are read by this layer. Architecture docs must describe variable names and config files only, not actual values.

### `telethon_manager/`

- `TelethonManagerSingleton` is the central in-memory registry for running clients, client configs, not-started configs, event handlers, running tasks, QR logins, and global running state.
- `telethon_client_config.py` defines the Pydantic `TelethonConfig` contract, including account type, API credentials, session string, bot token, phone, proxy, active state, and authorization type.
- `telethon_auth_drivers.py` supports console, phone, QR-code, and combined QR+phone authorization flows.
- `telethon_register_handlers.py` attaches Telethon handlers for NewMessage, MessageEdited, MessageRead, MessageDeleted, ChatAction, UserUpdate, CallbackQuery, InlineQuery, Album, and Raw events.
- `telethon_handlers/` contains per-event helpers.
- `telethon_attrs_chains/` contains attribute-chain definitions used to extract structured values from Telethon event objects.
- `telethon_qr_code_logins.py` keeps QR login state in a singleton.
- Bot-related informational identifiers are currently derived from the first 10 characters of the full bot token (for example in session naming, logs, and event payloads), not from the numeric bot ID segment before the token colon.
- `utils_specific/enrich_sender_profile_data.py` performs conservative sender-profile enrichment for message events. It fills only already-defined `tlt_sender_*` keys, first tries `event.get_sender()`, then falls back to `client.get_entity(sender_id)`, and never overwrites already-captured values.
- `hdr_helper_new_message.py` and `hdr_helper_message_edited.py` now call the sender-enrichment helper before webhook dispatch, which improves `username`, `first_name`, `last_name`, and occasionally `phone` completeness without changing the outgoing payload schema expected by the analytics service.

### `fast_api/`

The API is organized as many small `app_*` packages. Each package usually contains:

- `scheme_*.py`: Pydantic request models.
- `router_*.py`: `APIRouter` definitions.
- `helper_*.py`: endpoint-specific business logic, when needed.

All routers use the configured API base URL from `API_OPTIONS.API_BASE_URL_NAME`.

Current endpoint groups include:

- Health and Telethon task status.
- Start, stop, clear, and reconnect Telethon clients.
- Complete phone or QR-code authentication.
- Find Telegram users.
- Send Telegram messages and files.
- Get dialogs for selected configs, poll live dialog messages, and send dialog
  text/files to one selected peer.
- Get Telegram configs and message configs by web account.
- Activate/deactivate message-capable configs.
- Download/get files by Telegram message ID.
- Get locally saved files from the TLT server.
- Get S3-compatible storage objects or presigned URLs.
- Get generated QR-code images.

### Dialogs API v1

Dialogs API v1 is the contract used by the Globalhome website Dialogs page.
This service owns live Telethon-backed dialog discovery and short-poll live
message retrieval, while archive history remains in MessengerAgregator
Analytics.

Why this split exists:

- TLT manager already has connected Telethon clients and can inspect current
  dialogs and freshest messages.
- Analytics already stores normalized historical messages and is better suited
  for archive pagination.
- `messenger_type` must be validated as a real field now so the website does
  not hard-code a fake future-facing dropdown.

Dialogs-specific modules:

- `fast_api/app_dialogs_common/helper_dialogs_common.py`
- `fast_api/app_dialogs_by_configs/`
- `fast_api/app_dialog_messages_live/`
- `fast_api/app_send_dialog_message/`
- `fast_api/app_send_dialog_files/`
- `fast_api/_tests/test_dialogs_api_contract.py`

#### `POST /{API_BASE_URL_NAME}/get_dialogs_by_configs`

- Request body:
  - `auth_data.username`: `str`, required.
  - `auth_data.password`: `str`, required.
  - `web_account_data.web_account_id`: `str`, required.
  - `web_account_data.web_account_username`: `str`, required.
  - `dialogs_request_data.messenger_type`: `str`, required by contract;
    current supported value is `"telegram"`.
  - `dialogs_request_data.selected_configs`: `list[str]`, required and
    non-empty.
  - `dialogs_request_data.dialogs_limit_per_config`: `int`, optional, default
    `100`, must be positive.
- Response:
  - `message`: `str`.
  - `messenger_type`: `str`.
  - `web_account_id`: `str`.
  - `web_account_username`: `str`.
  - `selected_configs`: `list[str]`.
  - `missing_configs`: `list[str]`.
  - `dialogs_by_config`: `dict[str, list[dialog_item]]`.
- `dialog_item` fields:
  - `config_name`: `str`.
  - `peer_id`: `int`.
  - `peer_type`: `str`.
  - `peer_storage_type`: `str`.
  - `peer_key`: `str`.
  - `peer_title`: `str`.
  - `peer_username`: `str | null`.
  - `peer_first_name`: `str | null`.
  - `peer_last_name`: `str | null`.
  - `peer_phone`: `str | null`.
  - `peer_is_bot`: `bool`.
  - `can_send`: `bool`.
  - `unread_count`: `int`.
  - `is_pinned`: `bool`.
  - `last_message_id`: `int | null`.
  - `last_message_date`: `str | null`, ISO datetime.
  - `last_message_text`: `str`.
  - `last_message_out`: `bool`.
  - `has_draft`: `bool`.

#### `POST /{API_BASE_URL_NAME}/get_dialog_messages_live`

- Request body:
  - `auth_data.*`: required.
  - `web_account_data.*`: required.
  - `dialog_request_data.messenger_type`: `str`, required by contract.
  - `dialog_request_data.config_name`: `str`, required.
  - `dialog_request_data.peer_id`: `int`, required.
  - `dialog_request_data.peer_type`: `str`, required; validated against
    `user`, `chat`, `group`, `channel`, `bot`.
  - `dialog_request_data.peer_storage_type`: `str`, required; validated
    against `user`, `chat`, `channel`.
  - `dialog_request_data.after_message_id`: `int | null`, optional.
  - `dialog_request_data.messages_limit`: `int`, optional, default `50`.
- Response:
  - `message`: `str`.
  - `messenger_type`: `str`.
  - `config_name`: `str`.
  - `peer_id`: `int`.
  - `peer_type`: `str`.
  - `peer_storage_type`: `str`.
  - `after_message_id`: `int | null`.
  - `messages_limit`: `int`.
  - `returned_count`: `int`.
  - `latest_message_id`: `int`.
  - `live_messages`: `list[live_message]`.

#### `POST /{API_BASE_URL_NAME}/send_dialog_message`

- Request body:
  - `auth_data.*`: required.
  - `web_account_data.*`: required.
  - `send_dialog_message_data.messenger_type`: `str`, required.
  - `send_dialog_message_data.config_name`: `str`, required.
  - `send_dialog_message_data.peer_id`: `int`, required.
  - `send_dialog_message_data.peer_type`: `str`, required.
  - `send_dialog_message_data.peer_storage_type`: `str`, required.
  - `send_dialog_message_data.message_text`: `str`, required and non-empty
    after trimming.
- Response:
  - `message`: `str`.
  - `messenger_type`: `str`.
  - `config_name`: `str`.
  - `peer_id`: `int`.
  - `peer_type`: `str`.
  - `peer_storage_type`: `str`.
  - `sent_message`: `live_message`.

#### `POST /{API_BASE_URL_NAME}/send_dialog_files`

- Multipart form fields:
  - `auth_username`: `str`, required.
  - `auth_password`: `str`, required.
  - `web_account_id`: `str`, required.
  - `web_account_username`: `str`, required.
  - `messenger_type`: `str`, required.
  - `config_name`: `str`, required.
  - `peer_id`: `int`, required.
  - `peer_type`: `str`, required.
  - `peer_storage_type`: `str`, required.
  - `caption_text`: `str`, optional.
  - `files`: `file[]`, required.
- Response:
  - `message`: `str`.
  - `messenger_type`: `str`.
  - `config_name`: `str`.
  - `peer_id`: `int`.
  - `peer_type`: `str`.
  - `peer_storage_type`: `str`.
  - `sent_messages`: `list[live_message]`.

`live_message` fields used by both live polling and send responses:

- `config_name`: `str`.
- `peer_id`: `int`.
- `peer_type`: `str`.
- `peer_storage_type`: `str`.
- `message_id`: `int | null`.
- `sender_id`: `int | null`.
- `date`: `str | null`, ISO datetime.
- `edit_date`: `str | null`, ISO datetime.
- `text`: `str`.
- `raw_text`: `str`.
- `out`: `bool`.
- `from_me`: `bool`.
- `reply_to_msg_id`: `int | null`.
- `has_media`: `bool`.
- `media_type`: `str | null`.
- `file_name`: `str | null`.
- `file_mime_type`: `str | null`.
- `file_size`: `int | null`.

Dialogs-specific runtime behavior:

- `resolve_dialog_entity()` first tries `get_entity(peer_id)` and then falls
  back to iterating dialogs to disambiguate storage type.
- `can_send_to_entity()` allows users/chats/groups/bots and allows channels
  only when the current client appears to have posting rights.
- live updates are implemented with short polling through Telethon
  `get_messages(..., min_id=after_message_id)` rather than a websocket or
  push-broker layer.

### `db_postgres/`

- `postgres_conn/pgs_connection.py` defines async and sync SQLAlchemy engine singletons.
- `postgres_conn/postgres_session.py` wraps async and sync session lifecycle.
- `postgres_init/` initializes tables and creates default SQLAdmin users.
- `postgres_models/` contains SQLAlchemy ORM models:
  - `TelethonConfigModel` stores Telegram client config, credentials/session references, proxy config, active flags, and authorization type.
  - `AuthRoleModel` stores SQLAdmin/API authentication role data.
  - Mixins provide active/status and timestamp fields.
- `postgres_queries/` contains application-specific query functions for Telethon config caching, reading, and status/session updates.
- `postgres_queries_utils/` contains reusable flexible query builders and ORM update/save helpers.
- `postgres_tests/` contains existing database-oriented tests. New tests for Python packages should be placed in a package-local `_tests/` directory.

### `utils_specific/`

- `handle_all_event_params.py` builds normalized event payloads from Telethon events and client config data.
- `send_event_data_webhook.py` sends event payloads to the external aggregator API with configured credentials.
- `enrich_sender_profile_data.py` centralizes sender profile enrichment used by message-event handlers and is covered by package-local async unit tests in `utils_specific/_tests/`.
- `get_proxy_environ_conf.py` and `get_valid_proxy_config.py` convert configured proxy values into Telethon-compatible proxy tuples.
- `get_account_tlt_clients.py` selects usable account clients/configs for operations that require personal Telegram accounts.

### `s3_async_managers/`

- `AioBotoCoreManager` provides a reusable async context manager for an aiobotocore client.
- `get_s3_client()` provides a simple async context manager for one-off S3-compatible operations.
- S3 settings come from `.configs_s3_aws_api.ini` through `configs.environments`.

### `admin_panel/`

- `AdminAuthRoleAuthBackend` provides SQLAdmin authentication.
- `custom_templates/sqladmin/` overrides SQLAdmin templates and layout.
- `main.py` currently defines `admin_panel_views = []`; new SQLAdmin model views must be added there or by a future registration module.

## Data Flow

### Startup Flow

```text
main.py
|-- sync_initialize_db_tables()
|-- asyncio.run(main_process())
    |-- init_telethon_sessions_dir()
    |-- TelethonManagerSingleton.get_postgres_db_tlt_configs()
    |-- TelethonManagerSingleton.run_all_telethon_clients()
    |-- TelethonManagerSingleton.run_all_tlt_clients_async_tasks()
    |-- create_run_uvicorn_fastapi_server()
```

### Incoming Telegram Event Flow

```text
Telethon event
|-- registered handler in telethon_register_handlers.py
|-- telethon_handlers/hdr_helper_*.py
|-- telethon_attrs_chains/* for event-specific extraction
|-- utils_specific.handle_all_event_params.send_all_event_params()
|-- JSON-safe serialization
|-- utils_specific.send_event_data_webhook.send_event_data_webhook_req()
|-- external aggregator API
```

### Telegram Identity Data Availability

- Telegram `NewMessage` updates do not guarantee a full `User` payload for the sender. In many cases the event contains only peer identifiers such as `from_id` or `sender_id`.
- The project now uses two complementary strategies:
  - Passive extraction for message events through `telethon_attrs_chains/chain_message_new_edit.py`, which reads `sender.username`, `sender.first_name`, `sender.last_name`, and `sender.phone` when Telethon already has them in the event/cache.
  - Active lookup when fields are still missing: message handlers now use `utils_specific/enrich_sender_profile_data.py`, while other flows such as `ChatAction`, `UserUpdate`, and `fast_api/app_find_telegram_users_data/` call `get_entity(...)`, `contacts.ImportContactsRequest`, or `contacts.SearchRequest`.
- User phone numbers are the least reliable field. Telegram commonly exposes them only for the authenticated account itself, saved/imported contacts, or when privacy rules allow it. A message event alone should not be assumed to contain a sender phone number.
- For channel posts, anonymous admin posts, forwarded messages, and some bot/business contexts, the logical author may be a channel/signature/peer rather than a resolvable personal user profile.

### API Operation Flow

```text
FastAPI router
|-- Pydantic input schema
|-- endpoint helper or TelethonManagerSingleton method
|-- optional PostgreSQL query/session
|-- optional Telethon client operation
|-- optional local/S3 file operation
|-- response or HTTPException
```

## Technology Stack

- Python 3.12 runtime is implied by the checked-in virtual environment name.
- FastAPI, Starlette, Uvicorn for HTTP API serving.
- Telethon for Telegram user/bot clients and event handling.
- SQLAlchemy 2.x with asyncpg and psycopg2 for PostgreSQL access.
- SQLAdmin, WTForms, Jinja2, and Starlette sessions for the admin panel.
- Pydantic 2.x for request and internal data validation.
- aiobotocore/botocore for S3-compatible storage.
- MinIO via Docker Compose for local S3-compatible storage.
- httpx for outbound aggregator webhook calls.
- python-dotenv and ConfigParser-backed `.configs_*.ini` files for configuration.
- qrcode and Pillow for QR login image generation.
- bcrypt/argon2-related dependencies for password hashing/auth support.

## Configuration And Secrets

Configuration is split across `.env`, `.configs_*.ini`, and `docker_compose/.env`.

Known config files:

- `.configs_api.ini`
- `.configs_telegram.ini`
- `.configs_proxy.ini`
- `.configs_sqladmin.ini`
- `.configs_postgres.ini`
- `.configs_aggregator.ini`
- `.configs_s3_aws_api.ini`
- `docker_compose/.env`

These files may contain secrets such as API passwords, Telegram API hashes, bot tokens, PostgreSQL passwords, S3 keys, session keys, proxy credentials, and MinIO credentials. Do not copy secret values into Markdown docs, commits, logs, issues, tests, or generated examples.

Sensitive runtime files/directories:

- `TELETHON_SESSIONS/`
- `zTELETHON_SESSIONS_BACKUPS/`
- `TEMP_TELETHON_TEMP_FILES/`
- `TEMP_TELETHON_ARCHIVE_FILES/`
- `TEMP_QRCODE_IMAGES/`
- `zProxyBackup/`
- Any `.env` or `.configs_*.ini` file with real credentials.

## Architectural Patterns

- Singleton managers: `SingletonMeta` is used for shared Telethon and PostgreSQL engine state.
- Repository/query functions: database operations are separated into query modules and query utility modules.
- Router-per-feature API structure: each FastAPI feature is isolated in an `app_*` package.
- Pydantic contracts: request data and Telethon config data are validated through Pydantic models.
- Async-first runtime: Telethon, FastAPI, PostgreSQL async sessions, httpx, and S3 operations are designed around asyncio.
- Event adapter pattern: Telethon-specific event objects are converted into JSON-safe payloads before being sent to the external aggregator.
- Config-file based environment selection: runtime settings are selected from `.configs_*.ini` sections according to detected IP/platform.

## Architecture Decision Records

### ADR-001: Run Telethon clients and FastAPI in one asyncio process

Decision: The service starts Telethon clients first, then runs Uvicorn/FastAPI as an asyncio task in the same process.

Why: API endpoints need direct access to the in-memory `TelethonManagerSingleton` state and active `TelegramClient` objects. Keeping them in one process avoids IPC complexity and lets API operations manage live clients directly.

Consequences:

- Simpler operational model and direct in-memory coordination.
- A crash affects both API and Telethon clients.
- Long-running handlers must avoid blocking the event loop.

### ADR-002: Use PostgreSQL as source of truth for Telethon client configs

Decision: Telethon client configs are loaded from PostgreSQL through SQLAlchemy models and query functions.

Why: Telethon accounts/bots are operational entities that need persistent active flags, credentials/session references, message-use flags, and authorization metadata. PostgreSQL gives durable structured storage and query flexibility.

Consequences:

- Startup depends on PostgreSQL availability.
- DB schema and query helpers must stay synchronized with API and Telethon config contracts.
- Tests that touch this layer need an available test database or explicit mocks.

### ADR-003: Use SQLAlchemy async and sync engines

Decision: The project defines both `PgsAsyncConnection` and `PgsSyncConnection`.

Why: Most runtime operations are async, but table initialization and some admin/setup paths are sync-friendly. Keeping both engines supports startup initialization while allowing async API/runtime DB usage.

Consequences:

- Both engines must be closed during shutdown.
- Connection settings and pool options must remain consistent.

### ADR-004: Use SQLAdmin for administration

Decision: SQLAdmin is mounted into the FastAPI application with a custom authentication backend and templates.

Why: The service already uses SQLAlchemy models, so SQLAdmin can provide a lightweight admin interface without building a separate frontend.

Consequences:

- Admin auth/session settings are part of the FastAPI runtime.
- Model views must be explicitly registered.
- Templates under `admin_panel/custom_templates/sqladmin/` should be kept compatible with the installed SQLAdmin version.

### ADR-005: Use S3-compatible storage abstraction

Decision: The project uses aiobotocore helpers and a MinIO Docker Compose service for S3-compatible storage.

Why: Telegram media can be stored outside the application process while keeping local development possible through MinIO. S3-compatible APIs allow using MinIO locally and another compatible service in production.

Consequences:

- Media operations depend on configured endpoint, bucket, and credentials.
- Presigned URL/file retrieval helpers must not leak credentials.
- Local MinIO `.env` must be treated as sensitive.

### ADR-006: Forward Telegram events to an external aggregator API

Decision: Telethon event handlers serialize event data and send it to a configured external aggregator endpoint.

Why: This service acts as a Telegram ingestion/management layer while delegating downstream processing to an aggregator service.

Consequences:

- Event payloads must be JSON-safe.
- External API failures are currently logged and generally do not crash handlers.
- Credentials used for aggregator requests must remain out of documentation and commits.

### ADR-007: Keep configuration in local `.ini` files

Decision: The project uses `.configs_*.ini` files and `.env`, selected at runtime by IP/platform logic.

Why: The existing deployment style distinguishes local/test/production values without requiring a full configuration service.

Consequences:

- Config files are sensitive and must not be copied into docs.
- IP/platform selection logic should be tested carefully before deployment changes.
- Future agents should prefer adding new config keys to the existing config system instead of introducing another configuration mechanism.

### ADR-008: Accept partial Telegram identity data in event payloads

Decision: Incoming event payloads may contain only partial sender identity data, and downstream consumers must treat `username`, `first_name`, `last_name`, and `phone` as optional.

Why: Telegram and Telethon do not guarantee that every event includes a full sender `User` object. Some fields are absent because of update shape, cache state, entity availability, channel/anonymous posting semantics, or Telegram privacy restrictions. Phone availability is especially restricted.

Consequences:

- Event schemas and webhook consumers must treat sender profile fields as nullable.
- `NewMessage` and `MessageEdited` now perform an explicit enrichment step via `event.get_sender()` with `client.get_entity(sender_id)` fallback, while still treating all sender profile fields as nullable.
- Even with active enrichment, arbitrary users' phone numbers may remain unavailable.

### ADR-009: Split Dialogs archive and live sources by service responsibility

Decision: dialog archive history remains in MessengerAgregator Analytics, while
dialog discovery, live polling, and sending stay in TLT manager.

Why: Analytics already owns persisted normalized message history, while only
TLT manager has direct access to connected Telethon clients and real-time
message retrieval for currently running configs.

Consequences:

- the website merges archive and live results client-side;
- request fields such as `messenger_type`, `config_name`, `peer_type`, and
  `peer_storage_type` must stay stable across both services;
- live updates are near-real-time polling, not push delivery.

## Development Conventions

- Keep code comments, annotations, and commented notes in English.
- Keep `PROJECT_ARCHITECTURE.md` in English.
- Update `PROJECT_ARCHITECTURE.md` whenever code, structure, dependencies, runtime behavior, config conventions, or docs materially change.
- Do not store secrets or sensitive data in Markdown or documentation.
- Do not inspect or analyze `zBackUp/` and `zTest/`.
- Treat Telethon session files, proxy backups, `.env`, `.configs_*.ini`, and MinIO/DB credentials as sensitive.
- New tests for a Python package should go into a package-local `_tests/` directory.
- Do not commit unless explicitly requested. If commits are requested, generated commit messages must start with `AI_` and be split by meaning/category.
- Prefer existing helper modules and patterns over introducing new abstractions.
- Use async helpers for async runtime paths.
- Avoid blocking calls inside Telethon event handlers and FastAPI async endpoints.
- When exposing bot identity for logs, session names, or payload metadata, verify whether the code uses a truncated token prefix or the actual Telegram bot ID extracted from the token before `:`.

## Testing Notes

Existing tests are currently under `db_postgres/postgres_tests/`. The repository instruction says new tests should be placed in `_tests/` directories corresponding to each tested Python package. For future changes:

- Use focused tests near the package being changed, for example `fast_api/_tests/`, `telethon_manager/_tests/`, or `db_postgres/_tests/`.
- Mock Telethon clients, S3 clients, and external aggregator requests unless an integration test explicitly requires real services.
- Do not require real secrets in tests.
- Use test fixtures or environment overrides for PostgreSQL/S3 integration tests.

## Detailed Documentation References

- `_docs/_docs_server_linux/`: Linux service and startup examples.
- `_docs/_docs_server_linux/examples/`: systemd and daemon command examples.
- `_docs/_docs_event_params_descr/`: Telethon event parameter documentation.
- `docker_compose/docker-compose.yaml`: MinIO local S3-compatible storage service.
- `requirements.txt`: pinned dependency list.

## AI Agent Notes

- Always check this file before making project changes.
- If this file is missing, recreate it before other work.
- Before editing code, re-check the current project structure while excluding `zBackUp/` and `zTest/`.
- Keep this document synchronized with manual changes or pulled repository changes.
- Summarize architecture changes here, including the reason behind important decisions.
- Never paste actual secret values into this file.
