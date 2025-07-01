import yaml
import argparse
from typing import Any


def get_config_path() -> str:
    parser = argparse.ArgumentParser(
        add_help=False,
        description="Load configuration file path from CLI arguments."
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to the YAML configuration file (default: config.yaml)"
    )
    args, _ = parser.parse_known_args()
    return args.config


def load_yaml_config(path: str) -> dict[str, Any]:
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        raise FileNotFoundError(f"YAML config file not found: {path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file: {e}")

config_path = get_config_path()
raw_config = load_yaml_config(config_path)

# Top-level LSM9DS1 configuration dictionary
LSM9DS1_CONFIG: dict[str, Any] = raw_config.get("LSM9DS1_CONFIG", {})
