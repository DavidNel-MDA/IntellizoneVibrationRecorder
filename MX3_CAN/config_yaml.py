import argparse

import yaml
from bidict import bidict


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

MCP2515_CONFIG = raw_config["MCP2515_CONFIG"]

DISCOVERY_TIMEOUT = MCP2515_CONFIG.get("DISCOVERY_TIMEOUT", 300.0)
UID = MCP2515_CONFIG["UID"]
BITRATE = MCP2515_CONFIG["BITRATE"]

MODULE_TYPE = bidict(MCP2515_CONFIG["MODULE_TYPE"])
CONTROLLER_MESSAGE_TYPE = bidict(MCP2515_CONFIG["CONTROLLER_MESSAGE_TYPE"])

GLOBAL_ZONE_STATUS = MCP2515_CONFIG["GLOBAL_ZONE_STATUS"]
OCTANT_LOCATION = MCP2515_CONFIG["OCTANT_LOCATION"]
SCREEN_ORIENTATION = MCP2515_CONFIG["SCREEN_ORIENTATION"]
STATUS_LEVEL = MCP2515_CONFIG["STATUS_LEVEL"]
OPERATOR_PRESENCE = MCP2515_CONFIG["OPERATOR_PRESENCE"]
SYNC_RATE = MCP2515_CONFIG["SYNC_RATE"]
PROXIMITY_SYNC_RATE = MCP2515_CONFIG["PROXIMITY_SYNC_RATE"]
ENABLED_STATUS = MCP2515_CONFIG["ENABLED_STATUS"]
LOCATOR_FAILURE_TYPES = MCP2515_CONFIG["LOCATOR_FAILURE_TYPES"]
LOCATOR_UPDATE_TYPES = MCP2515_CONFIG["LOCATOR_UPDATE_TYPES"]
