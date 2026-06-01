from pathlib import Path
import unittest


ROOT_DIR = Path(__file__).resolve().parents[2] / "docker_compose"
POSTGRES_COMPOSE = ROOT_DIR / "docker-compose_postgres.yaml"
MINIO_COMPOSE = ROOT_DIR / "docker-compose_s3_minio.yaml"
POSTGRES_RUNBOOK = ROOT_DIR / "POSTGRES_RUNBOOK.md"
MINIO_RUNBOOK = ROOT_DIR / "S3_MINIO_RUNBOOK.md"


class DockerComposeConfigTests(unittest.TestCase):
    def test_postgres_compose_contains_required_startup_contract(self):
        text = POSTGRES_COMPOSE.read_text(encoding="utf-8")

        required_fragments = [
            "name: octadim_postgres",
            "init-postgres-dir:",
            "postgres:",
            "image: postgres:16-alpine",
            "condition: service_completed_successfully",
            "${POSTGRES_DATA_DIR:?err_POSTGRES_DATA_DIR_is_required}",
            "${POSTGRES_USER:?err_POSTGRES_USER_is_required}",
            "${POSTGRES_PASSWORD:?err_POSTGRES_PASSWORD_is_required}",
            "${POSTGRES_HOST:-127.0.0.1}:${POSTGRES_PORT:-5432}:5432",
            "PGDATA: /var/lib/postgresql/data/pgdata",
            "pg_isready -h 127.0.0.1",
            "postgres_network:",
        ]

        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)

    def test_minio_compose_contains_required_startup_contract(self):
        text = MINIO_COMPOSE.read_text(encoding="utf-8")

        required_fragments = [
            "name: octadim_s3_minio",
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

        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)

    def test_runbooks_reference_expected_env_files_and_validation_commands(self):
        postgres_text = POSTGRES_RUNBOOK.read_text(encoding="utf-8")
        minio_text = MINIO_RUNBOOK.read_text(encoding="utf-8")

        self.assertIn("--env-file .env.postgres", postgres_text)
        self.assertIn("docker-compose -f docker-compose_postgres.yaml", postgres_text)
        self.assertIn("config --quiet", postgres_text)

        self.assertIn("--env-file .env.s3_minio", minio_text)
        self.assertIn("docker-compose -f docker-compose_s3_minio.yaml", minio_text)
        self.assertIn("config --quiet", minio_text)


if __name__ == "__main__":
    unittest.main()
