#!/home/matrixdesign/IntellizoneVibrationRecorder/.venv/bin/python3
import logging
import time
import can
import argparse

from MX3_CAN.config_yaml import UID, MODULE_TYPE, CONTROLLER_MESSAGE_TYPE
from MX3_CAN.can_interface import CANInterface
from MX3_CAN.messages import SendMessage
from MX3_CAN.status_listener import StatusListener
from MX3_CAN.status_request import request_controller_status
from MX3_CAN.node_discovery import (
    wait_for_configuration_write,
    send_periodic_node_discovery,
    log_timeout_error,
)


# Command-line interface for verbosity
parser = argparse.ArgumentParser(description="MX3 IntelliZone CAN Device")
parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
args = parser.parse_args()

logging_level = logging.DEBUG if args.verbose else logging.INFO
logging.basicConfig(
    level=logging_level, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def initialize_can_interface() -> can.BusABC:
    """
    Initialize the CAN interface and bring it up.

    Returns the active CAN bus interface.
    """
    # Create a CAN interface object
    can_if: CANInterface = CANInterface()
    # Bring up the CAN interface
    can_bus: can.BusABC = can_if.bring_up()
    # Return the active CAN bus interface
    return can_bus


def perform_node_discovery(canbus: can.BusABC, uid: list[int]) -> int:
    """
    Perform node discovery.

    This function sends periodic Node Discovery messages until a Configuration Write message is received.

    Parameters
    ----------
    canbus : can.BusABC
        The active CAN bus interface.
    uid : list of int
        The device's Unique ID.

    Returns
    -------
    int
        The assigned Node ID.
    """
    # Start sending periodic Node Discovery messages
    discovery_task = send_periodic_node_discovery(canbus, uid)
    try:
        # Wait for a Configuration Write message and extract the assigned Node ID
        node_id = wait_for_configuration_write(canbus, uid)
        logger.info(f"Node Discovery complete. Assigned ID: 0x{node_id:X}")
        return node_id
    finally:
        # Stop sending periodic Node Discovery messages
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
        The assigned Node ID.

    Returns
    -------
    can.AsyncBufferedSendTask
        The periodic sender task handle.
    """
    # Create a SendMessage object configured to send Heartbeat messages with the
    # assigned Node ID.
    heartbeat_sender = SendMessage(
        message_type=CONTROLLER_MESSAGE_TYPE["Heartbeat"],
        node_id=node_id,
        module_type=MODULE_TYPE["Status_Screen"],
        dest_module=MODULE_TYPE["Controller"],
        dest_node=0x0,
    )
    # Start sending periodic Heartbeat messages on the CAN bus.
    return heartbeat_sender.send_periodic(canbus, data=[], period=0.2)


def setup_status_listener(
    canbus: can.BusABC,
    node_id: int,
) -> tuple[StatusListener, can.Notifier]:
    """
    Set up a StatusListener to receive Device Status Report messages from the
    controller on the CAN bus and a Notifier to forward received messages to
    the listener.

    Parameters
    ----------
    canbus : can.BusABC
        The active CAN bus interface.
    node_id : int
        The assigned Node ID.

    Returns
    -------
    tuple[StatusListener, can.Notifier]
        A tuple containing the StatusListener object and the Notifier.
    """
    # Create a StatusListener object configured to receive messages from the
    # controller with the Device_Status_Report message type.
    listener = StatusListener(
        node_id=node_id,
        expected_reply=CONTROLLER_MESSAGE_TYPE["Device_Status_Report"],
        module_type=MODULE_TYPE["Status_Screen"],
        source_module=MODULE_TYPE["Controller"],
        source_node=0x0,
    )
    # Create a Notifier that calls the listener when a message is received on
    # the CAN bus.
    notifier = can.Notifier(canbus, [listener])

    # Return the StatusListener object and the Notifier as a tuple.
    return listener, notifier


def main() -> None:
    """
    Main function for the IntelliZone CAN device implementation.

    This function is called when the script is run directly.
    """
    logger.info("Starting IntelliZone CAN device implementation.")

    while True:
        can_notifier = None
        can_interface = None
        heartbeat_task = None
        status_listener = None
        can_bus = None

        try:
            # 1. Initialize CAN
            can_interface = CANInterface()
            can_bus = can_interface.bring_up()
            logger.info("Initialized CAN bus interface.")

            # 2. Node discovery (may raise TimeoutError)
            node_id = perform_node_discovery(can_bus, UID)
            logger.info(f"Assigned Node ID: 0x{node_id:X}")

            # 3. Heartbeat
            heartbeat_task = start_heartbeat(can_bus, node_id)
            logger.info("Started periodic heartbeat task.")

            # 4. Listener + notifier
            status_listener, can_notifier = setup_status_listener(can_bus, node_id)
            logger.info("Set up status listener and Notifier.")

            # 5. Status request loop
            request_controller_status(can_bus, node_id, status_listener)
            logger.info("Sending periodic status requests to the controller.")

            logger.info("Running... Press Ctrl+C to exit.")
            while True:
                time.sleep(1)

        except TimeoutError as timeout_error:
            # Handle node discovery timeouts
            logger.warning(f"TimeoutError: {timeout_error}. Restarting in 5 seconds...")
            log_timeout_error(f"TimeoutError: {timeout_error}")
            time.sleep(5)
            continue

        except Exception as general_error:
            # Handle any other exceptions
            logger.exception(f"Fatal Error: {general_error}")
            logger.error("Unhandled exception. Exiting.")
            break

        finally:
            # Clean up after any exceptions
            if can_notifier:
                can_notifier.stop()
                logger.info("Stopped notifier.")
            if heartbeat_task:
                heartbeat_task.stop()
                logger.info("Stopped heartbeat task.")
            if status_listener:
                status_listener.close_logger()
            if can_bus:
                try:
                    can_bus.shutdown()  # <-- NEW: Ensure raw socket is released properly
                    logger.info("Shutdown CAN bus.")
                except Exception as e:
                    logger.warning("Could not shutdown CAN bus cleanly: %s", e)
            if can_interface:
                can_interface.shutdown()
                logger.info("Cleaned up CAN interface.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Interrupted by user. Exiting...")
