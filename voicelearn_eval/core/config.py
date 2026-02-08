"""Configuration loading and management."""

from dataclasses import dataclass
from pathlib import Path

import yaml

DEFAULT_DATA_DIR = Path.home() / ".voicelearn-eval"
DEFAULT_DB_PATH = DEFAULT_DATA_DIR / "data.db"


@dataclass
class AppConfig:
    """Application configuration."""

    db_path: Path = DEFAULT_DB_PATH
    data_dir: Path = DEFAULT_DATA_DIR
    api_port: int = 3201
    web_port: int = 3200
    host: str = "127.0.0.1"
    gpu_device: str = "auto"
    batch_size: int = 8
    timeout_per_benchmark: int = 3600
    ci_mode: bool = False
    ci_min_score: float = 60.0
    ci_fail_on_regression: bool = True
    ci_regression_threshold: float = 0.10

    @classmethod
    def from_yaml(cls, path: Path) -> "AppConfig":
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                if key in ("db_path", "data_dir"):
                    setattr(config, key, Path(value))
                else:
                    setattr(config, key, value)
        return config

    @classmethod
    def from_defaults(cls) -> "AppConfig":
        return cls()


def load_config(config_path: str | None = None) -> AppConfig:
    """Load configuration from YAML file or defaults."""
    if config_path:
        return AppConfig.from_yaml(Path(config_path))
    return AppConfig.from_defaults()


def ensure_data_dir(config: AppConfig) -> None:
    """Create data directory if it doesn't exist."""
    config.data_dir.mkdir(parents=True, exist_ok=True)
    config.db_path.parent.mkdir(parents=True, exist_ok=True)
