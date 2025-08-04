import os
import time
from datetime import datetime

import can

from MX3_CAN.config_yaml import (CONTROLLER_MESSAGE_TYPE, DISCOVERY_TIMEOUT,
                                 MODULE_TYPE)
from MX3_CAN.messages import SendMessage

ERROR_LOG_BASE = "error_log_"


def get_daily_error_log_filename():
    """Generate filename for today's error log."""
    return f"{ERROR_LOG_BASE}{datetime.now().strftime('%Y-%m-%d')}.log"


def log_timeout_error(message: str):
    os.makedirs("logs", exist_ok=True)  # Ensure folder exists
    log_file = os.path.join(
        "logs", f"error_log_{datetime.now().strftime('%Y-%m-%d')}.log"
    )
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"{timestamp} - {message}\n")


def send_periodic_node_discovery(
    can_bus: can.BusABC,
    device_uid: list[int],
    temporary_node_id: int = 0xF,
    local_module: str = "Status_Screen",
):
    discovery_payload = device_uid + [0x01, 0x00, 0x01, 0x00]
    # Build the Node Discovery message
    sender = SendMessage(
        message_type=CONTROLLER_MESSAGE_TYPE["Node_Discovery"],
        node_id=temporary_node_id,
        module_type=MODULE_TYPE[local_module],
        dest_module=MODULE_TYPE["Controller"],
        dest_node=0x0,
    )

    # Send the message every 100 ms
    return sender.send_periodic(can_bus, data=discovery_payload, period=0.1)


def wait_for_configuration_write(
    canbus: can.BusABC,
    device_uid: list[int],
    temporary_node_id: int = 0xF,
    local_module: str = "Status_Screen",
) -> int:
    start_time = time.time()

    # Build the expected Configuration Write message
    expected_message = SendMessage(
        message_type=CONTROLLER_MESSAGE_TYPE["Config_Write"],
        node_id=temporary_node_id,
        module_type=MODULE_TYPE[local_module],
        dest_module=MODULE_TYPE["Controller"],
        dest_node=0x0,
        direction="rx",
    )

    # Calculate the expected arbitration ID
    expected_arbitration_id = expected_message.build_arbitration_id()

    # Wait indefinitely for the Configuration Write message
    while time.time() - start_time < DISCOVERY_TIMEOUT:
        message = canbus.recv()
        if message and message.arbitration_id == expected_arbitration_id:
            # Extract the assigned node ID from the message
            data = list(message.data)
            if data[0] == 0x00 and data[1:5] == device_uid:
                node_id = data[5]
                return node_id

    # Log and raise timeout if no message is received within the specified time
    log_timeout_error("Timeout waiting for Configuration Write message.")
    raise TimeoutError("Timed out after 5 minutes waiting for Configuration Write.")
