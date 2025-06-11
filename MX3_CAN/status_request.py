import logging
from messages import SendMessage
from can import BusABC, CanError
from status_listener import StatusListener
from config import CONTROLLER_MESSAGE_TYPE, MODULE_TYPE


logger = logging.getLogger(__name__)

def request_controller_status(
    can_bus: BusABC,
    node_id: int,
    status_listener: StatusListener,
    local_module_type: str = "Status_Screen"
) -> None:
    """
    Continuously sends Status_Read_Request messages until a response is received.

    Parameters
    ----------
    can_bus : BusABC
        The active CAN bus interface.
    node_id : int
        The device's assigned Node ID.
    status_listener : StatusListener
        A StatusListener object that sets an event once a valid response is received.
    local_module_type : str, optional
        Module type of the sending device (e.g., 'Status_Screen'). Defaults to "Status_Screen".

    Returns
    -------
    None
    """
    if can_bus is None or node_id is None:
        # Check for valid CAN bus and Node ID
        logger.error("Invalid CAN bus or node ID.")
        return

    # Create a SendMessage object for Status_Read_Request
    sender = SendMessage(
        message_type=CONTROLLER_MESSAGE_TYPE["Status_Read_Request"],
        node_id=node_id,
        module_type=MODULE_TYPE[local_module_type],
        dest_module=MODULE_TYPE["Controller"],
        dest_node=0x0
    )

    # Continuously send the message every 2 seconds until a response is received
    while not status_listener.received_event.is_set():
        try:
            # Build and send the message
            msg = sender.build_message([0x00])
            can_bus.send(msg)
            logger.info(f"Sent Controller Status Request: {msg}")
        except CanError:
            # Handle CAN bus send error
            logger.error("Failed to send Controller Status request.")
        # Wait for 2 seconds before the next attempt
        status_listener.received_event.wait(timeout=2.0)
