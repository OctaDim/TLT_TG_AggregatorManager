from configparser import ConfigParser
from pathlib import Path
import unittest


ROOT_DIR = Path(__file__).resolve().parents[2]
SAMPLES_DIR = ROOT_DIR / "_docs" / "tlt_sensitive_config_samples"

ROOT_CONFIG_PAIRS = [
    (ROOT_DIR / ".configs_aggregator.ini", SAMPLES_DIR / "root_configs" / ".configs_aggregator.ini.example"),
    (ROOT_DIR / ".configs_api.ini", SAMPLES_DIR / "root_configs" / ".configs_api.ini.example"),
    (ROOT_DIR / ".configs_postgres.ini", SAMPLES_DIR / "root_configs" / ".configs_postgres.ini.example"),
    (ROOT_DIR / ".configs_proxy.ini", SAMPLES_DIR / "root_configs" / ".configs_proxy.ini.example"),
    (ROOT_DIR / ".configs_s3_aws_api.ini", SAMPLES_DIR / "root_configs" / ".configs_s3_aws_api.ini.example"),
    (ROOT_DIR / ".configs_sqladmin.ini", SAMPLES_DIR / "root_configs" / ".configs_sqladmin.ini.example"),
    (ROOT_DIR / ".configs_telegram.ini", SAMPLES_DIR / "root_configs" / ".configs_telegram.ini.example"),
]

ENV_FILE_PAIRS = [
    (ROOT_DIR / "docker_compose" / ".env_local_postgres", SAMPLES_DIR / "docker_compose" / ".env_local_postgres.example"),
    (ROOT_DIR / "docker_compose" / ".env.ip_postgres", SAMPLES_DIR / "docker_compose" / ".env.ip_postgres.example"),
    (ROOT_DIR / "docker_compose" / ".env_local_s3_minio", SAMPLES_DIR / "docker_compose" / ".env_local_s3_minio.example"),
    (ROOT_DIR / "docker_compose" / ".env.ip_s3_minio", SAMPLES_DIR / "docker_compose" / ".env.ip_s3_minio.example"),
    (ROOT_DIR / "docker_compose" / ".env_local_rabbitmq_aiopika", SAMPLES_DIR / "docker_compose" / ".env_local_rabbitmq_aiopika.example"),
    (ROOT_DIR / "docker_compose" / ".env.ip_rabbitmq_aiopika", SAMPLES_DIR / "docker_compose" / ".env.ip_rabbitmq_aiopika.example"),
]

SENSITIVE_KEY_PARTS = (
    "ACCESS_KEY",
    "API_HASH",
    "API_ID",
    "COOKIE",
    "DEFAULT_PASS",
    "DEFAULT_USER",
    "PASSWORD",
    "SECRET",
    "SESSION_KEY",
    "USERNAME",
)


def read_ini_shape(path):
    parser = ConfigParser()
    parser.optionxform = str
    parser.read(path, encoding="utf-8")
    return {
        section: set(parser[section].keys())
        for section in parser.sections()
    }


def read_ini_values(path):
    parser = ConfigParser()
    parser.optionxform = str
    parser.read(path, encoding="utf-8")
    return {
        key: value
        for section in parser.sections()
        for key, value in parser[section].items()
    }


def read_env_file(path):
    values = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition("=")
        if separator:
            values[key.strip()] = value.strip()
    return values


class SensitiveConfigSampleTests(unittest.TestCase):
    def test_root_ini_samples_match_real_file_shapes(self):
        for real_path, sample_path in ROOT_CONFIG_PAIRS:
            with self.subTest(real_file=real_path.name):
                self.assertTrue(real_path.exists())
                self.assertTrue(sample_path.exists())
                self.assertEqual(read_ini_shape(real_path), read_ini_shape(sample_path))

    def test_env_samples_match_real_file_keys(self):
        for real_path, sample_path in ENV_FILE_PAIRS:
            with self.subTest(real_file=real_path.name):
                self.assertTrue(real_path.exists())
                self.assertTrue(sample_path.exists())
                self.assertEqual(set(read_env_file(real_path)), set(read_env_file(sample_path)))

    def test_sample_values_are_realistic_examples(self):
        sample_files = [sample for _, sample in ROOT_CONFIG_PAIRS + ENV_FILE_PAIRS]

        for sample_path in sample_files:
            with self.subTest(sample_file=sample_path.name):
                sample_values = read_env_file(sample_path)
                if sample_path.suffix == ".example" and sample_path.name.startswith(".configs_"):
                    sample_values = read_ini_values(sample_path)

                self.assertTrue(sample_values)
                for key, value in sample_values.items():
                    with self.subTest(sample_file=sample_path.name, key=key):
                        self.assertTrue(value)
                        self.assertNotIn("REPLACE_ME", value)
                        self.assertNotIn("<", value)
                        self.assertNotIn(">", value)

    def test_sensitive_example_values_do_not_match_real_values(self):
        file_pairs = ROOT_CONFIG_PAIRS + ENV_FILE_PAIRS

        for real_path, sample_path in file_pairs:
            real_values = read_env_file(real_path)
            sample_values = read_env_file(sample_path)
            if sample_path.suffix == ".example" and sample_path.name.startswith(".configs_"):
                real_values = read_ini_values(real_path)
                sample_values = read_ini_values(sample_path)

            for key, sample_value in sample_values.items():
                if not any(part in key.upper() for part in SENSITIVE_KEY_PARTS):
                    continue

                real_value = real_values.get(key, "")
                if not real_value:
                    continue

                with self.subTest(sample_file=sample_path.name, key=key):
                    self.assertNotEqual(real_value, sample_value)


if __name__ == "__main__":
    unittest.main()
