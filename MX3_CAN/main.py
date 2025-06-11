#!/home/matrixdesign/IntellizoneVibrationRecorder/.venv/bin/python3
import logging
import time
import can

from config import UID, MODULE_TYPE, CONTROLLER_MESSAGE_TYPE
from can_interface import CANInterface
from messages import SendMessage
from status_listener import StatusListener
from status_request import request_controller_status
from node_discovery import wait_for_configuration_write, send_periodic_node_discovery


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def initialize_can_interface() -> can.BusABC:
    """
    Bring up the CAN interface and return a can.BusABC object.

    The returned BusABC object is a representation of the CAN interface,
    which can be used for sending and receiving CAN messages.

    Returns
    -------
    can_bus: can.BusABC
        The active CAN bus interface.
    """
    can_if: CANInterface = CANInterface()
    can_bus: can.BusABC = can_if.bring_up()
    return can_bus


def perform_node_discovery(canbus: can.BusABC, uid: list[int]) -> int:
    """
    Perform Node Discovery, sending Node Discovery messages and waiting for
    a Configuration Write message from the controller.

    Parameters
    ----------
    canbus : can.BusABC
        The active CAN bus interface.
    uid : list[int]
        The 4-byte Unique ID of this device.

    Returns
    -------
    int
        The assigned Node ID from the controller.
    """
    discovery_task = send_periodic_node_discovery(canbus, uid)
    try:
        node_id = wait_for_configuration_write(canbus, uid)
        logger.info(f"Node Discovery complete. Assigned ID: 0x{node_id:X}")
        return node_id
    finally:
        if discovery_task:
            discovery_task.stop()
            logger.info("Stopped periodic Node Discovery.")


def start_heartbeat(canbus: can.BusABC, node_id: int):
    """
    Start sending periodic Heartbeat messages to the controller.

    Parameters
    ----------
    canbus : can.BusABC
        The active CAN bus interface.
    node_id : int
        The assigned Node ID from the controller.

    Returns
    -------
    task : can.AsyncBufferedSendTask
        The periodic send task, or None on failure.
    """
    heartbeat_sender = SendMessage(
        message_type=CONTROLLER_MESSAGE_TYPE["Heartbeat"],
        node_id=node_id,
        module_type=MODULE_TYPE["Status_Screen"],
        dest_module=MODULE_TYPE["Controller"],
        dest_node=0x0,
    )
    return heartbeat_sender.send_periodic(canbus, data=[], period=0.2)


def setup_status_listener(
    canbus: can.BusABC,  # The active CAN bus interface
    node_id: int,  # The assigned Node ID from the controller
) -> tuple[StatusListener, can.Notifier]:
    """
    Set up a StatusListener object and a Notifier that calls the listener when a
    message is received on the CAN bus.

    The Notifier is configured to call the StatusListener object when a message is
    received on the CAN bus. The StatusListener object is configured to expect
    messages from the controller with the Device_Status_Report message type.

    Parameters
    ----------
    canbus : can.BusABC
        The active CAN bus interface.
    node_id : int
        The assigned Node ID from the controller.

    Returns
    -------
    tuple[StatusListener, can.Notifier]
        A tuple containing the StatusListener object and the Notifier.
    """
    listener = StatusListener(
        node_id=node_id,
        expected_reply=CONTROLLER_MESSAGE_TYPE["Device_Status_Report"],
        module_type=MODULE_TYPE["Status_Screen"],
        source_module=MODULE_TYPE["Controller"],
        source_node=0x0,
    )
    notifier = can.Notifier(canbus, [listener])
    return listener, notifier


def main() -> None:
    """
    Main entry point for the IntelliZone CAN device implementation.

    This function performs the following steps:

    1. Initializes the CAN interface.
    2. Performs node discovery.
    3. Starts the heartbeat task.
    4. Sets up a status listener.
    5. Sends periodic status requests to the controller.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    logger.info("Starting IntelliZone CAN device implementation.")

    # Bring up the CAN interface
    can_if: CANInterface = CANInterface()
    canbus: can.BusABC = can_if.bring_up()

    # Perform node discovery
    # Replace UID with your actual variable
    node_id: int = perform_node_discovery(canbus, UID)
    logger.info(f"Assigned Node ID: 0x{node_id:X}")

    # Start the heartbeat task
    heartbeat_task: can.Bus.send_periodic = start_heartbeat(canbus, node_id)
    logger.info("Started heartbeat task.")

    # Set up a status listener
    listener, notifier = setup_status_listener(canbus, node_id)
    logger.info("Set up status listener.")

    # Send periodic status requests to the controller
    request_controller_status(canbus, node_id, listener)
    logger.info("Sending periodic status requests to the controller.")

    try:
        logger.info("Running... Press Ctrl+C to exit.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
    finally:
        # Stop the notifier first to prevent it from accessing a closed socket
        if notifier:
            notifier.stop()
            logger.info("Stopped notifier.")

        # Then stop the heartbeat task
        if heartbeat_task:
            heartbeat_task.stop()
            logger.info("Stopped heartbeat task.")

        listener.close_logger()

        # Finally, bring down the CAN interface
        can_if.shutdown()
        logger.info("Cleaned up resources.")


if __name__ == "__main__":
    main()
