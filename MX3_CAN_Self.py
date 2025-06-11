#!/home/matrixdesign/IntellizoneVibrationRecorder/.venv/bin/python3

import os
import time
import can
import subprocess
import threading

# Configuration parameters
UID = [0x45, 0x2F, 0xA7, 0xA2]                  # Replace with real UID
MODULE_TYPE = 0xC                               # Status Screen
BITRATE = 125000

CONTROLLER_MESSAGE_TYPE = {
    "Config_Write":	            0x1F1E,
    "Config_Write_Ext":	        0x1F1F,
    "Device_Error_Report":	    0x1F5A,
    "Device_Error_Report_Ext":	0x1F5B,
    "Device_Status_Report":	    0x1F78,
    "Device_Status_Report_Ext":	0x1F79,
    "Config_Response":	        0x1F96,
    "Config_Response_Ext":	    0x1F97,
    "Node_Discovery":	        0x1FA0,
    "Config_Read_Request":	    0x1FD2,
    "Config_Read_Request_Ext":	0x1FD3,
    "Status_Read_Request":	    0x1FDC,
    "Status_Read_Request_Ext":	0x1FDD,
    "Heartbeat":	            0x1FE3,
    "Device_Command":	        0x1FF0,
}

class StatusListener(can.Listener):
    def __init__(self, node_id, expected_reply):
        self.node_id = node_id
        self.expected_reply_prefix = ( expected_reply << 16) | (0x30 << 8) | (MODULE_TYPE << 4) | node_id
        self.received_event = threading.Event()

    def on_message_received(self, msg):
        if (msg.arbitration_id >> 8) == (self.expected_reply_prefix >> 8):
            print(f"Received status message: {msg}")
            self.received_event.set()
            
            
        
def bring_can_up():
    """
    Bring up the CAN interface (currently hard-coded as 'can0') and return
    a can.Bus object. This function will retry setting up the CAN interface
    if the initial attempt fails. The bitrate is set to the value specified
    in the BITRATE constant.
    """
    try:
        os.system(f"sudo ip link set can0 up type can bitrate {BITRATE}")
    except subprocess.CalledProcessError:
        print("CAN interface 'can0' setup failed. Retrying.")
        os.system(f"sudo ip link set can0 up type can bitrate {BITRATE}")
    canbus = can.Bus(interface='socketcan', channel='can0', bitrate=BITRATE)
    print("CAN interface up.")
    return canbus

def bring_can_down(canbus):
    """
    Shut down the CAN interface and bring down the CAN network interface.
    This function closes the provided can.Bus object and executes a system 
    command to disable the CAN interface (hard-coded as 'can0'). It ensures 
    the CAN interface is properly deactivated.
    """
    if canbus:
        canbus.shutdown()
    os.system("sudo ip link set can0 down")
    print("CAN interface down.")
    
def send_node_discovery(canbus, uid):
    """
    Start sending periodic Node Discovery messages to the CAN bus.

    Parameters
    ----------
    canbus : can.Bus
        The CAN bus to send on.
    uid : list of 4 int
        The 4-byte Unique ID of this device.

    Returns
    -------
    task : can.Bus
        The Task object representing the periodic sender, or None on failure.
    """
    if canbus is None:
        print("CAN bus not initialized.")
        return None

    payload = uid + [0x01, 0x00, 0x01, 0x00]    # UID + Protocol & App version
    msg = can.Message(
        arbitration_id=0x1FA0CF30,
        data=payload,
        is_extended_id=True
    )

    try:
        task = canbus.send_periodic(msg, 0.1)
        print(f"Started periodic Node Discovery: {msg}")
        return task
    except can.CanError:
        print("Failed to start periodic Node Discovery.")
        return None

def wait_for_config_write(canbus, expected_uid):
    """
    Wait for the controller to send a Configuration Write message with the
    assigned Node ID for this device.

    Parameters
    ----------
    canbus : can.Bus
        The CAN bus to listen on.
    expected_uid : list of 4 int
        The 4-byte Unique ID of this device.

    Returns
    -------
    assigned_node_id : int
        The assigned Node ID from the controller.
    """
    print("Waiting for Configuration Write from controller...")
    still_waiting = True
    while still_waiting:
        msg = canbus.recv()                     # blocking wait
        if msg and msg.arbitration_id == 0x1F1E30CF:
            data = list(msg.data)
            if data[0] == 0x00 and data[1:5] == expected_uid:
                assigned_node_id = data[5]
                print(f"Config received. Assigned Node ID: 0x{assigned_node_id:X}")
                still_waiting = False
                return assigned_node_id
            
def send_heartbeat(
    canbus: can.BusABC,  # The CAN bus to send on
    node_id: int     # The assigned Node ID from the controller
) -> can.Bus.send_periodic:
    """
    Start sending periodic Heartbeat messages to the controller.

    Parameters
    ----------
    canbus : can.Bus
        The CAN bus to send on.
    node_id : int
        The assigned Node ID from the controller.

    Returns
    -------
    task : can.Bus.send_periodic
        The periodic send task, or None on failure.
    """
    if canbus is None:
        print("CAN bus not initialized.")
        return None

    # MatrixCAN Heartbeat ID: 0x1FE3XXY0
    module_type = MODULE_TYPE                   # 0xC for Status Screen
    dest_module = 0x3                           # Controller
    dest_node = 0x0                             # Default

    arb_id = (0x1FE3 << 16) | (module_type << 12) | (node_id << 8) | (dest_module << 4) | dest_node

    msg = can.Message(
        arbitration_id=arb_id,
        data=[],                                # heartbeat payload is empty
        is_extended_id=True
    )

    try:
        task = canbus.send_periodic(msg, 0.2)   # Every 200 ms
        print(f"Started periodic Heartbeat: {msg}")
        return task
    except can.CanError:
        print("Failed to start periodic Heartbeat.")
        return None
        

def request_status(
    canbus: can.BusABC,  # The CAN bus to send on
    node_id: int,        # The assigned Node ID from the controller
    listener: StatusListener,  # StatusListener object to set an event when a response is received
    expected_prefix: int  # The expected arbitration ID prefix for the response
) -> None:
    """
    Continuously sends Status_Read_Request messages until a response is received.

    Parameters
    ----------
    canbus : can.BusABC
        The CAN bus to send on.
    node_id : int
        The assigned Node ID from the controller.
    listener : StatusListener
        A StatusListener object that sets an event once a valid response is received.
    expected_prefix : int
        The expected arbitration ID prefix for the response.

    Returns
    -------
    None
    """
    if canbus is None or node_id is None:
        return None

    module_type = MODULE_TYPE
    dest_module = 0x3
    dest_node = 0x0
    status_arb_id = (expected_prefix << 16) | (module_type << 12) | (node_id << 8) | (dest_module << 4) | dest_node

    print("Sending controller status request every 2 seconds until a response is received...")

    try:
        while not listener.received_event.is_set():
            msg = can.Message(arbitration_id=status_arb_id, data=[0x00], is_extended_id=True)
            try:
                canbus.send(msg)
                print(f"Sent Controller Status Request: {msg}")
            except can.CanError:
                print("Failed to send Controller Status request.")
            listener.received_event.wait(timeout=2.0)
    except KeyboardInterrupt:
        print("Interrupted by user.")


def main() -> None:
    """
    Main entry point for the MX3 CAN device implementation.

    This function brings up the CAN bus, starts the Node Discovery process,
    waits for the controller to assign a Node ID, starts the Heartbeat task,
    sets up a listener and notifier for the controller status, and starts
    sending status requests every 2 seconds until a response is received.
    """
    canbus: can.BusABC = bring_can_up()
    discovery_task: can.Bus.send_periodic = send_node_discovery(canbus, UID)

    try:
        node_id = wait_for_config_write(canbus, UID)
        if node_id is None:
            print("Error: failed to receive Node ID from controller")
            # handle the error case
        else:
            print(f"Node Discovery complete. Assigned ID: 0x{node_id:X}")
        print(f"Node Discovery complete. Assigned ID: 0x{node_id:X}")
    finally:
        if discovery_task:
            discovery_task.stop()
            print("Stopped periodic Node Discovery.")

    if node_id is not None:
        heartbeat_task: can.Bus.send_periodic = send_heartbeat(canbus, node_id)

        # Set up listener and notifier
        controller_listener: StatusListener = StatusListener(node_id, CONTROLLER_MESSAGE_TYPE["Device_Status_Report"])
        notifier: can.Notifier = can.Notifier(canbus, [controller_listener])

        # Start sending status requests
        request_status(canbus, node_id, controller_listener, CONTROLLER_MESSAGE_TYPE["Status_Read_Request"])

        try:
            print("Running... Press Ctrl+C to exit.")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Interrupted by user.")
        finally:
            if heartbeat_task:
                heartbeat_task.stop()
                print("Stopped periodic Heartbeat.")
            notifier.stop()
            bring_can_down(canbus)
    else:
        print("Error: Node ID is None, cannot send heartbeat.")

if __name__ == "__main__":
    main()