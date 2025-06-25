import yaml
from bidict import bidict
import argparse

def get_config_path() -> str:
    """
    Parse the command-line argument for the config path.

    The --config argument is parsed from sys.argv. If not provided, it defaults to
    'config.yaml'.

    Returns:
        str: The path to the config file.
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        description="Parse command-line arguments for the device configuration.",
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to the YAML configuration file.",
    )
    args, _ = parser.parse_known_args()
    return args.config


config_path = get_config_path()

with open(config_path, "r") as f:
    raw_config = yaml.safe_load(f)

LSM9DS1_CONFIG = raw_config["LSM9DS1_CONFIG"]

ACCELEROMETER_ADDRESS = LSM9DS1_CONFIG["ACCELEROMETER_ADDRESS"]
ACCELEROMETER_GYROSCOPE_REGISTER = bidict(LSM9DS1_CONFIG["ACCELEROMETER_GYROSCOPE_REGISTER"])
MAGNETOMETER_REGISTER = bidict(LSM9DS1_CONFIG["MAGNETOMETER_REGISTER"])