import can
from messages import SendMessage
import logging
from datetime import datetime
import time
from MX3_CAN.config_yaml import CONTROLLER_MESSAGE_TYPE, MODULE_TYPE, DISCOVERY_TIMEOUT

ERROR_LOG_BASE = "error_log_"

def get_daily_error_log_filename():
    """Generate filename for today's error log."""
    return f"{ERROR_LOG_BASE}{datetime.now().strftime('%Y-%m-%d')}.log"

def log_timeout_error(message):
    """Log error to the daily file with timestamp."""
    with open(get_daily_error_log_filename(), "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")

def send_periodic_node_discovery(
    can_bus: can.BusABC,
    device_uid: list[int],
    temporary_node_id: int = 0xF,
    local_module: str = "Status_Screen"
):
    """
    Starts periodic Node Discovery messages on the CAN bus.

    Sends a Node Discovery message every 100 ms to the CAN bus. The message
    contains the device's Unique ID, along with the temporary Node ID assigned
    by the device before the controller assigns a new one.

    Parameters
    ----------
    can_bus : can.BusABC
        The active CAN bus interface.
    device_uid : list[int]
        4-byte Unique ID of this device.
    temporary_node_id : int
        Temporary node ID before being assigned by controller (default 0xF).
    local_module : str
        Name of the local module type (e.g., 'Status_Screen').

    Returns
    -------
    can.bus.AsyncBufferedSendTask
        Periodic sender task handle.
    """
    discovery_payload = device_uid + [0x01, 0x00, 0x01, 0x00]
    # Build the Node Discovery message
    sender = SendMessage(
        message_type=CONTROLLER_MESSAGE_TYPE["Node_Discovery"],
        node_id=temporary_node_id,
        module_type=MODULE_TYPE[local_module],
        dest_module=MODULE_TYPE["Controller"],
        dest_node=0x0
    )

    # Send the message every 100 ms
    return sender.send_periodic(can_bus, data=discovery_payload, period=0.1)


def wait_for_configuration_write(
    canbus: can.BusABC,
    device_uid: list[int],
    temporary_node_id: int = 0xF,
    local_module: str = "Status_Screen"
) -> int:
    """
    Waits for a Configuration Write message from the controller and retrieves
    the assigned node ID for the device.

    The function waits indefinitely until a Configuration Write message is
    received that matches the given device UID and temporary node ID. It then
    extracts the assigned node ID from the message and returns it.

    Parameters
    ----------
    canbus : can.BusABC
        The active CAN bus interface to listen on.
    device_uid : list[int]
        The 4-byte unique ID of this device.
    temporary_node_id : int, optional
        Temporary node ID for the device before being assigned by the
        controller (default is 0xF).
    local_module : str, optional
        Name of the local module type (e.g., 'Status_Screen').

    Returns
    -------
    int
        The assigned node ID from the controller.

    Raises
    ------
    TimeoutError
        If the operation times out while waiting for the Configuration Write
        message.
    """
    start_time = time.time()

    # Build the expected Configuration Write message
    expected_message = SendMessage(
        message_type=CONTROLLER_MESSAGE_TYPE["Config_Write"],
        node_id=temporary_node_id,
        module_type=MODULE_TYPE[local_module],
        dest_module=MODULE_TYPE["Controller"],
        dest_node=0x0,
        direction="rx"
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
