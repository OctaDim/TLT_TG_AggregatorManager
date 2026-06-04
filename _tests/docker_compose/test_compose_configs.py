from pathlib import Path
import unittest


ROOT_DIR = Path(__file__).resolve().parents[2] / "docker_compose"

POSTGRES_COMPOSE_FILES = [
    ROOT_DIR / "local_docker-compose_postgres.yaml",
    ROOT_DIR / "ip_docker-compose_postgres.yaml",
]
MINIO_COMPOSE_FILES = [
    ROOT_DIR / "local_docker-compose_s3_minio.yaml",
    ROOT_DIR / "ip_docker-compose_s3_minio.yaml",
]
RABBITMQ_AIOPIKA_COMPOSE_FILES = [
    ROOT_DIR / "local_docker-compose-rabbitmq_aiopika.yaml",
    ROOT_DIR / "ip_docker-compose-rabbitmq_aiopika.yaml",
]
SSHPASS_COMPOSE_FILES = [
    ROOT_DIR / "local_docker-compose_sshpass.yaml",
    ROOT_DIR / "ip_docker-compose_sshpass.yaml",
]
POSTGRES_RUNBOOK = ROOT_DIR / "POSTGRES_RUNBOOK.md"
MINIO_RUNBOOK = ROOT_DIR / "S3_MINIO_RUNBOOK.md"
RABBITMQ_AIOPIKA_RUNBOOK = ROOT_DIR / "RABBITMQ_AIOPIKA_RUNBOOK.md"
SSHPASS_RUNBOOK = ROOT_DIR / "SSHPASS_RUNBOOK.md"


class DockerComposeConfigTests(unittest.TestCase):
    def test_active_compose_files_use_local_or_ip_prefix(self):
        compose_files = sorted(ROOT_DIR.glob("*docker-compose*.yaml"))

        self.assertTrue(compose_files)

        for compose_file in compose_files:
            with self.subTest(compose_file=compose_file.name):
                self.assertTrue(
                    compose_file.name.startswith(("local_", "ip_")),
                    msg=f"{compose_file.name} must start with local_ or ip_",
                )

    def test_postgres_compose_files_contain_required_startup_contract(self):
        expected_names = {
            "local_docker-compose_postgres.yaml": "name: octadim_local_postgres",
            "ip_docker-compose_postgres.yaml": "name: octadim_ip_postgres",
        }

        required_fragments = [
            "init-postgres-dir:",
            "postgres:",
            "image: postgres:16-alpine",
            "condition: service_completed_successfully",
            "${POSTGRES_DATA_DIR:?err_POSTGRES_DATA_DIR_is_required}",
            "${POSTGRES_USER:?err_POSTGRES_USER_is_required}",
            "${POSTGRES_PASSWORD:?err_POSTGRES_PASSWORD_is_required}",
            "${POSTGRES_HOST:-127.0.0.1}:${POSTGRES_PORT:-5432}:5432",
            "PGDATA: /var/lib/postgresql/data/pgdata",
            "command -v psql",
            "command -v pg_isready",
            "pg_isready -h 127.0.0.1",
            "postgres_network:",
        ]

        for compose_file in POSTGRES_COMPOSE_FILES:
            text = compose_file.read_text(encoding="utf-8")
            with self.subTest(compose_file=compose_file.name, fragment="name"):
                self.assertIn(expected_names[compose_file.name], text)

            for fragment in required_fragments:
                with self.subTest(compose_file=compose_file.name, fragment=fragment):
                    self.assertIn(fragment, text)

    def test_sshpass_compose_files_contain_required_startup_contract(self):
        expected_names = {
            "local_docker-compose_sshpass.yaml": "name: octadim_local_sshpass",
            "ip_docker-compose_sshpass.yaml": "name: octadim_ip_sshpass",
        }

        required_fragments = [
            "sshpass-tools:",
            "image: alpine:3.20",
            "apk add --no-cache openssh-client sshpass",
            "command -v sshpass",
            "command -v ssh",
            "sshpass -V",
            "tail -f /dev/null",
        ]

        for compose_file in SSHPASS_COMPOSE_FILES:
            text = compose_file.read_text(encoding="utf-8")
            with self.subTest(compose_file=compose_file.name, fragment="name"):
                self.assertIn(expected_names[compose_file.name], text)

            for fragment in required_fragments:
                with self.subTest(compose_file=compose_file.name, fragment=fragment):
                    self.assertIn(fragment, text)

    def test_minio_compose_files_contain_required_startup_contract(self):
        expected_names = {
            "local_docker-compose_s3_minio.yaml": "name: octadim_local_s3_minio",
            "ip_docker-compose_s3_minio.yaml": "name: octadim_ip_s3_minio",
        }

        required_fragments = [
            "init-minio-dir:",
            "minio:",
            "create-minio-buckets:",
            "image: minio/minio:latest",
            "image: minio/mc:latest",
            "condition: service_completed_successfully",
            "condition: service_healthy",
            "${MINIO_DATA_DIR:?err_MINIO_DATA_DIR_is_required}",
            "${MINIO_ROOT_USER:?err_MINIO_ROOT_USER_is_required}",
            "${MINIO_ROOT_PASSWORD:?err_MINIO_ROOT_PASSWORD_is_required}",
            "${MINIO_EXTERNAL_IP:-0.0.0.0}:${MINIO_API_PORT:-9000}:9000",
            "${MINIO_EXTERNAL_IP:-0.0.0.0}:${MINIO_CONSOLE_PORT:-9001}:9001",
            "mc",
            "ready",
            "local",
            "mc alias set local http://minio:9000",
            "mc mb --ignore-existing",
            "minio_network:",
        ]

        for compose_file in MINIO_COMPOSE_FILES:
            text = compose_file.read_text(encoding="utf-8")
            with self.subTest(compose_file=compose_file.name, fragment="name"):
                self.assertIn(expected_names[compose_file.name], text)

            for fragment in required_fragments:
                with self.subTest(compose_file=compose_file.name, fragment=fragment):
                    self.assertIn(fragment, text)

    def test_rabbitmq_aiopika_compose_files_contain_required_startup_contract(self):
        expected_names = {
            "local_docker-compose-rabbitmq_aiopika.yaml": "name: octadim_local_rabbitmq_aiopika",
            "ip_docker-compose-rabbitmq_aiopika.yaml": "name: octadim_ip_rabbitmq_aiopika",
        }

        required_fragments = [
            "init-rabbitmq-dir:",
            "rabbitmq:",
            "image: rabbitmq:3.13-management-alpine",
            "condition: service_completed_successfully",
            "${RABBITMQ_DATA_DIR:?err_RABBITMQ_DATA_DIR_is_required}",
            "${RABBITMQ_DEFAULT_USER:?err_RABBITMQ_DEFAULT_USER_is_required}",
            "${RABBITMQ_DEFAULT_PASS:?err_RABBITMQ_DEFAULT_PASS_is_required}",
            "${RABBITMQ_ERLANG_COOKIE:?err_RABBITMQ_ERLANG_COOKIE_is_required}",
            "${RABBITMQ_EXTERNAL_IP:-127.0.0.1}:${RABBITMQ_AMQP_PORT:-5672}:5672",
            "${RABBITMQ_EXTERNAL_IP:-127.0.0.1}:${RABBITMQ_MANAGEMENT_PORT:-15672}:15672",
            "rabbitmq-diagnostics -q ping",
            "rabbitmq_aiopika_network:",
        ]

        for compose_file in RABBITMQ_AIOPIKA_COMPOSE_FILES:
            text = compose_file.read_text(encoding="utf-8")
            with self.subTest(compose_file=compose_file.name, fragment="name"):
                self.assertIn(expected_names[compose_file.name], text)

            for fragment in required_fragments:
                with self.subTest(compose_file=compose_file.name, fragment=fragment):
                    self.assertIn(fragment, text)

    def test_runbooks_reference_expected_split_env_files_and_validation_commands(self):
        runbook_expectations = [
            (
                POSTGRES_RUNBOOK,
                [
                    "local_docker-compose_postgres.yaml --env-file .env_local_postgres",
                    "ip_docker-compose_postgres.yaml --env-file .env.ip_postgres",
                    "config --quiet",
                ],
            ),
            (
                MINIO_RUNBOOK,
                [
                    "local_docker-compose_s3_minio.yaml --env-file .env_local_s3_minio",
                    "ip_docker-compose_s3_minio.yaml --env-file .env.ip_s3_minio",
                    "config --quiet",
                ],
            ),
            (
                RABBITMQ_AIOPIKA_RUNBOOK,
                [
                    "local_docker-compose-rabbitmq_aiopika.yaml --env-file .env_local_rabbitmq_aiopika",
                    "ip_docker-compose-rabbitmq_aiopika.yaml --env-file .env.ip_rabbitmq_aiopika",
                    "config --quiet",
                ],
            ),
            (
                SSHPASS_RUNBOOK,
                [
                    "local_docker-compose_sshpass.yaml",
                    "ip_docker-compose_sshpass.yaml",
                    "config --quiet",
                    "docker exec local-sshpass-tools-octadim sshpass -V",
                    "docker exec ip-sshpass-tools-octadim sshpass -V",
                ],
            ),
        ]

        for runbook, fragments in runbook_expectations:
            text = runbook.read_text(encoding="utf-8")
            for fragment in fragments:
                with self.subTest(runbook=runbook.name, fragment=fragment):
                    self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
