import yaml
from bidict import bidict
import argparse


# Parse command-line arguments for config path
def get_config_path() -> str:
    """
    Parse the command-line argument for the config path.

    The --config argument is parsed from sys.argv. If not provided, it defaults to
    'config.yaml'.

    Returns:
        str: The path to the config file.
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
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

DISCOVERY_TIMEOUT = raw_config.get("DISCOVERY_TIMEOUT", 300.0)
UID = raw_config["UID"]
BITRATE = raw_config["BITRATE"]

MODULE_TYPE = bidict(raw_config["MODULE_TYPE"])
CONTROLLER_MESSAGE_TYPE = bidict(raw_config["CONTROLLER_MESSAGE_TYPE"])

GLOBAL_ZONE_STATUS = raw_config["GLOBAL_ZONE_STATUS"]
OCTANT_LOCATION = raw_config["OCTANT_LOCATION"]
SCREEN_ORIENTATION = raw_config["SCREEN_ORIENTATION"]
STATUS_LEVEL = raw_config["STATUS_LEVEL"]
OPERATOR_PRESENCE = raw_config["OPERATOR_PRESENCE"]
SYNC_RATE = raw_config["SYNC_RATE"]
PROXIMITY_SYNC_RATE = raw_config["PROXIMITY_SYNC_RATE"]
ENABLED_STATUS = raw_config["ENABLED_STATUS"]
LOCATOR_FAILURE_TYPES = raw_config["LOCATOR_FAILURE_TYPES"]
LOCATOR_UPDATE_TYPES = raw_config["LOCATOR_UPDATE_TYPES"]
