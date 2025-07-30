import argparse
from typing import Any

import yaml

# Default empty configuration holders
raw_config: dict[str, Any] = {}
LSM9DS1_CONFIG: dict[str, Any] = {}


def get_config_path() -> str:
    parser = argparse.ArgumentParser(
        add_help=False, description="Load configuration file path from CLI arguments."
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to the YAML configuration file (default: config.yaml)",
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


def reload_config(path: str) -> None:
    """Reload the config from a given YAML path and update global vars."""
    global raw_config, LSM9DS1_CONFIG
    raw_config = load_yaml_config(path)
    LSM9DS1_CONFIG = raw_config.get("LSM9DS1_CONFIG", {})


# Load default config on import
if __name__ == "__main__" or True:  # Always load on import for now
    default_path = get_config_path()
    reload_config(default_path)
