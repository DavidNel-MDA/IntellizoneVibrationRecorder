from MX3_CAN.config_yaml import *
import logging

logger = logging.getLogger(__name__)

def safe_get(data: list[int], index: int, default: int = 0) -> int:
    """Safely retrieve a byte from a list of bytes, with a default value if the index is out of bounds."""
    return data[index] if index < len(data) else default


def parse_tracking_status(
    data_bytes: list[int], 
    status_store: dict[str, dict[str, str]]
) -> dict[str, dict[str, str]]:
    """
    Parse tracking status from data bytes.

    Data format:
    - Byte 0: Parameter code (0x10)
    - Byte 1:
        Bits 7-6: Global Zone Status
        Bit 5: Operator Present
        Bits 4-2: Octant Location
        Bits 1-0: Screen Orientation
    - Bytes 2–4: Closest Locator ID (24-bit MSB)
    - Byte 5:
        Bits 7-5: Octant Location
        Bits 1-0: Screen Orientation
    """
    if not data_bytes:
        return status_store

    try:
        byte1 = safe_get(data_bytes, 1)
        byte2 = safe_get(data_bytes, 2)
        byte3 = safe_get(data_bytes, 3)
        byte4 = safe_get(data_bytes, 4)
        byte5 = safe_get(data_bytes, 5)

        # Extract bit fields
        global_zone_status_code = (byte1 >> 6) & 0b11
        operator_presence_code = (byte1 >> 5) & 0b1

        # Closest Locator ID (3 bytes: byte2, byte3, byte4)
        closest_locator_id = f"{(byte2 << 16 | byte3 << 8 | byte4):06X}"

        octant_location_code = (byte5 >> 5) & 0b111
        screen_orientation_code = byte5 & 0b11

        # Map codes to human-readable statuses
        parsed_status = {
            "Global Zone Status": STATUS_LEVEL.get(global_zone_status_code, "Unknown"),
            "Operator Present": OPERATOR_PRESENCE.get(operator_presence_code, "Unknown"),
            "Closest Locator ID": closest_locator_id,
            "Octant Location": OCTANT_LOCATION.get(octant_location_code, "Unknown"),
            "Screen Orientation": SCREEN_ORIENTATION.get(screen_orientation_code, "Unknown")
        }

        status_store.setdefault("Tracking Status", {})

        for key, value in parsed_status.items():
            if status_store["Tracking Status"].get(key) != value:
                status_store["Tracking Status"][key] = value

    except Exception as e:
        logger.exception(f"Error parsing tracking status: {e}")

    return status_store




def operator_mnid(
    data_bytes: list[int], 
    status_store: dict[str, dict[str, str]]
) -> dict[str, dict[str, str]]:
    """
    Parses the operator MNID from the given data bytes and updates the status store.

    Parameters
    ----------
    data_bytes : list[int]
        A list of integers representing the data bytes to be parsed.
    status_store : dict[str, dict[str, str]]
        A dictionary containing the current status store, which will be updated
        with the parsed operator MNID information.

    Returns
    -------
    dict[str, dict[str, str]]
        The updated status store with the latest operator MNID information.
    """
    if not data_bytes:
        return status_store

    try:
        operator_mnid_keys = ["Operator MNID 1", "Operator MNID 2", "Operator MNID 3"]
        parsed_mnid = {
            operator_mnid_keys[i]: f"{safe_get(data_bytes, 2 * i + 1):02X}{safe_get(data_bytes, 2 * i + 2):02X}"
            for i in range(3)
        }

        status_store.setdefault("Operator MNID", {})

        for key, value in parsed_mnid.items():
            if status_store["Operator MNID"].get(key) != value:
                status_store["Operator MNID"][key] = value

    except (IndexError, TypeError):
        pass

    return status_store



def parse_diagnostic_information(
    data_bytes: list[int],
    status_store: dict[str, dict[str, str]]
) -> dict[str, dict[str, str]]:
    """Parse diagnostic information from a list of data bytes and update the status store."""
    if not data_bytes or not status_store:
        return status_store

    diagnostic_info = {}

    try:
        byte_1 = data_bytes[1]
        byte_2 = data_bytes[2]

        diagnostic_info["Global System Status"] = GLOBAL_ZONE_STATUS.get((byte_1 >> 6) & 0b11, "Unknown")
        diagnostic_info["Driver 0 Status"] = GLOBAL_ZONE_STATUS.get((byte_2 >> 6) & 0b11, "Unknown")
        diagnostic_info["Driver 1 Status"] = GLOBAL_ZONE_STATUS.get((byte_2 >> 4) & 0b11, "Unknown")
        diagnostic_info["Driver 2 Status"] = GLOBAL_ZONE_STATUS.get((byte_2 >> 2) & 0b11, "Unknown")
        diagnostic_info["Driver 3 Status"] = GLOBAL_ZONE_STATUS.get(byte_2 & 0b11, "Unknown")

        if "Diagnostic Information" not in status_store:
            status_store["Diagnostic Information"] = {}

        for key, value in diagnostic_info.items():
            if status_store["Diagnostic Information"].get(key) != value:
                status_store["Diagnostic Information"][key] = value

    except (IndexError, TypeError):
        pass

    return status_store



def parse_can_bus_status(
    data_bytes: list[int],
    status_store: dict[str, dict[str, str]]
) -> dict[str, dict[str, str]]:
    """Parse CAN bus status from a list of data bytes and update the status store."""

    if not data_bytes or not status_store:
        return status_store

    try:
        can_bus_status = {}

        can_bus_status["Vortex CAN Bus Status"] = GLOBAL_ZONE_STATUS.get(data_bytes[1], "Unknown")
        can_bus_status["AVR CAN Bus Status"] = GLOBAL_ZONE_STATUS.get(data_bytes[2], "Unknown")

        if "CANBus Status" not in status_store:
            status_store["CANBus Status"] = {}

        for key, value in can_bus_status.items():
            if status_store["CANBus Status"].get(key) != value:
                status_store["CANBus Status"][key] = value

    except (IndexError, TypeError):
        pass

    return status_store



def parse_rf_module_status(
    data_bytes: list[int],
    status_store: dict[str, dict[str, str]]
) -> dict[str, dict[str, str]]:
    """
    Parse RF module status from a list of data bytes and update the status store.

    This function takes a list of data bytes and a status store dictionary as input,
    and returns an updated status store with the parsed RF module status information.

    The function extracts the serial communications status, Mnet connection status,
    and wireless AVR error code status from the data bytes, and updates the status
    store with these values if they have changed.

    Parameters
    ----------
    data_bytes : list[int]
        A list of integers representing the data bytes to be parsed.
    status_store : dict[str, dict[str, str]]
        A dictionary containing the current status store, which will be updated
        with the parsed RF module status information.

    Returns
    -------
    dict[str, dict[str, str]]
        The updated status store with the latest RF module status information.
    """
    if not data_bytes:
        return status_store

    parsed_status = {}

    try:
        # Extract the serial communications status, Mnet connection status, and
        # wireless AVR error code status from the data bytes
        parsed_status["SerialCommsStatus"] = GLOBAL_ZONE_STATUS.get(data_bytes[1], "Unknown")
        parsed_status["MnetConnectionStatus"] = GLOBAL_ZONE_STATUS.get(data_bytes[2], "Unknown")
        parsed_status["WirelessAvrErrorCodeStatus"] = GLOBAL_ZONE_STATUS.get(data_bytes[3], "Unknown")

        # Update the status store with the parsed status information
        status_key = "RFModuleStatus"

        if status_key not in status_store:
            status_store[status_key] = {}

        for key, value in parsed_status.items():
            if status_store[status_key].get(key) != value:
                status_store[status_key][key] = value

    except (IndexError, TypeError):
        # Handle potential exceptions from safe_get or dictionary operations
        pass

    return status_store


def parse_controller_status(
    data_bytes: list[int],
    status_store: dict[str, dict[str, str]]
) -> dict[str, dict[str, str]]:
    """
    Parse controller status from a list of data bytes and update the status store.

    This function takes a list of data bytes and a status store dictionary as input,
    and returns an updated status store with the parsed controller status information.

    The function extracts the controller version status, vortex board version status,
    KeyLok authentication status, soft PLC comms status, CAN serial number status,
    MML RF signal detection status, MML mag signal detection driver 0 status,
    MML mag signal detection driver 1 status, MML mag signal detection driver 2 status,
    and MML mag signal detection driver 3 status from the data bytes, and updates the status
    store with these values if they have changed.

    Parameters
    ----------
    data_bytes : list[int]
        A list of integers representing the data bytes to be parsed.
    status_store : dict[str, dict[str, str]]
        A dictionary containing the current status store, which will be updated
        with the parsed controller status information.

    Returns
    -------
    dict[str, dict[str, str]]
        The updated status store with the latest controller status information.
    """
    if not data_bytes or not status_store:
        return status_store

    controller_status = {}

    try:
        # Extract the controller version status, vortex board version status,
        # KeyLok authentication status, soft PLC comms status, CAN serial number status,
        # MML RF signal detection status, MML mag signal detection driver 0 status,
        # MML mag signal detection driver 1 status, MML mag signal detection driver 2 status,
        # and MML mag signal detection driver 3 status from the data bytes
        byte1 = data_bytes[1]
        byte2 = data_bytes[2]
        byte3 = data_bytes[3]
        byte4 = data_bytes[4]

        controller_status["Controller Version Status"] = GLOBAL_ZONE_STATUS.get((byte1 >> 6) & 0b11, "Unknown")
        controller_status["Vortex Board Version Status"] = GLOBAL_ZONE_STATUS.get((byte1 >> 2) & 0b11, "Unknown")

        controller_status["KeyLok Authentication Status"] = GLOBAL_ZONE_STATUS.get((byte2 >> 6) & 0b11, "Unknown")
        controller_status["Soft PLC Comms Status"] = GLOBAL_ZONE_STATUS.get((byte2 >> 2) & 0b11, "Unknown")

        controller_status["CAN Serial Number Status"] = GLOBAL_ZONE_STATUS.get((byte3 >> 6) & 0b11, "Unknown")
        controller_status["MML RF Signal Detection Status"] = GLOBAL_ZONE_STATUS.get((byte3 >> 2) & 0b11, "Unknown")

        controller_status["MML Mag Signal Detection Driver 0 Status"] = GLOBAL_ZONE_STATUS.get((byte4 >> 6) & 0b11, "Unknown")
        controller_status["MML Mag Signal Detection Driver 1 Status"] = GLOBAL_ZONE_STATUS.get((byte4 >> 4) & 0b11, "Unknown")
        controller_status["MML Mag Signal Detection Driver 2 Status"] = GLOBAL_ZONE_STATUS.get((byte4 >> 2) & 0b11, "Unknown")
        controller_status["MML Mag Signal Detection Driver 3 Status"] = GLOBAL_ZONE_STATUS.get(byte4 & 0b11, "Unknown")

        # Update the status store with the parsed status information
        if "Controller Status" not in status_store:
            status_store["Controller Status"] = {}

        for key, value in controller_status.items():
            if status_store["Controller Status"].get(key) != value:
                status_store["Controller Status"][key] = value

    except (IndexError, TypeError):
        # Handle potential exceptions from safe_get or dictionary operations
        pass

    return status_store




def parse_proximity_sensor_status(
    data_bytes: list[int],
    status_store: dict[str, dict[str, str]]
) -> dict[str, dict[str, str]]:
    """
    Parse proximity sensor status from a list of data bytes and update the status store.

    The function takes a list of data bytes and a status store dictionary as input,
    and returns an updated status store with the parsed proximity sensor status information.

    The function extracts the sync rate, locator test status, sync rate status,
    locator wave set status, locator battery voltage status, locator no FPGA interrupt status,
    and locator driver distance status from the data bytes, and updates the status store
    with these values if they have changed.

    Parameters
    ----------
    data_bytes : list[int]
        A list of integers representing the data bytes to be parsed.
    status_store : dict[str, dict[str, str]]
        A dictionary containing the current status store, which will be updated
        with the parsed proximity sensor status information.

    Returns
    -------
    dict[str, dict[str, str]]
        The updated status store with the latest proximity sensor status information.
    """
    if not data_bytes or not status_store:
        return status_store

    byte_1 = safe_get(data_bytes, 1)
    byte_2 = safe_get(data_bytes, 2)
    byte_3 = safe_get(data_bytes, 3)

    parsed_status = {
        "SyncRate": PROXIMITY_SYNC_RATE.get((byte_1 >> 4) & 0b1111, "Unknown"),
        "LocatorTestStatus": GLOBAL_ZONE_STATUS.get((byte_1 >> 2) & 0b11, "Unknown"),
        "SyncRateStatus": GLOBAL_ZONE_STATUS.get(byte_1 & 0b11, "Unknown"),
        "LocatorWaveSetStatus": GLOBAL_ZONE_STATUS.get((byte_2 >> 6) & 0b11, "Unknown"),
        "LocatorBatteryVoltageStatus": GLOBAL_ZONE_STATUS.get((byte_2 >> 2) & 0b11, "Unknown"),
        "LocatorNoFPGAIntStatus": GLOBAL_ZONE_STATUS.get((byte_3 >> 6) & 0b11, "Unknown"),
        "LocatorDriverDistanceStatus": GLOBAL_ZONE_STATUS.get((byte_3 >> 2) & 0b11, "Unknown")
    }

    status_key = "ProximitySensorStatus"
    if status_key not in status_store:
        status_store[status_key] = {}

    for key, value in parsed_status.items():
        if status_store[status_key].get(key) != value:
            status_store[status_key][key] = value

    return status_store



def parse_coil_driver_status(data_bytes: list[int], status_store: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    """
    Parse coil driver status from a list of data bytes and update the status store.

    The function takes a list of data bytes and a status store dictionary as input,
    and returns an updated status store with the parsed coil driver status information.

    The function extracts the serial comms status, signal open status, signal short status,
    power open status, power short status, driver enable status, and 72V supply status from the
    data bytes, and updates the status store with these values if they have changed.

    Parameters
    ----------
    data_bytes : list[int]
        A list of integers representing the data bytes to be parsed.
    status_store : dict[str, dict[str, str]]
        A dictionary containing the current status store, which will be updated
        with the parsed coil driver status information.

    Returns
    -------
    dict[str, dict[str, str]]
        The updated status store with the latest coil driver status information.
    """
    if not data_bytes or not status_store:
        return status_store

    parsed_status = {}

    # Extract coil driver status
    for byte_index, byte_name in enumerate(["Serial Comms", "Signal Open", "Signal Short", "Power Open", "Power Short"]):
        parsed_status.update(
            {
                # Shift the byte value by 6 - i * 2 to get the status for the i-th driver
                f"{byte_name.title()} Driver {i}": GLOBAL_ZONE_STATUS.get(
                    (data_bytes[byte_index + 1] >> (6 - i * 2)) & 0b11, "Unknown"
                )
                for i in range(4)
            }
        )

    # Extract additional coil driver status
    parsed_status.update(
        {
            "Driver Enable 0": ENABLED_STATUS.get((data_bytes[6] >> 7) & 0b01, "Unknown"),
            "Driver Enable 1": ENABLED_STATUS.get((data_bytes[6] >> 5) & 0b01, "Unknown"),
            "Driver Enable 2": ENABLED_STATUS.get((data_bytes[6] >> 3) & 0b01, "Unknown"),
            "Driver Enable 3": ENABLED_STATUS.get((data_bytes[6] >> 1) & 0b01, "Unknown"),
            "72V Supply Status": GLOBAL_ZONE_STATUS.get((data_bytes[7] >> 2) & 0b11, "Unknown"),
        }
    )

    # Update the status store
    status_key = "Coil Driver Status"
    if status_key not in status_store:
        status_store[status_key] = {}

    for key, value in parsed_status.items():
        if status_store[status_key].get(key) != value:
            status_store[status_key][key] = value

    return status_store



def parse_digital_io_status(
    data_bytes: list[int],
    status_store: dict[str, dict[str, str]]
) -> dict[str, dict[str, str]]:
    """Parse digital IO status from a list of data bytes and update the status store.

    The function takes a list of data bytes and a status store dictionary as input,
    and returns an updated status store with the parsed digital IO status information.

    The function extracts the status of digital inputs 0-9 and digital outputs 0-3 from
    the data bytes, and updates the status store with these values if they have changed.

    Parameters
    ----------
    data_bytes : list[int]
        A list of integers representing the data bytes to be parsed.
    status_store : dict[str, dict[str, str]]
        A dictionary containing the current status store, which will be updated
        with the parsed digital IO status information.

    Returns
    -------
    dict[str, dict[str, str]]
        The updated status store with the latest digital IO status information.
    """
    if not data_bytes or not status_store:
        return status_store

    digital_io_status = {}

    # Inputs 0–9 (first 10 bits of a 2-byte field)
    for i in range(10):
        # Extract the i-th bit of the input byte
        input_bit = (data_bytes[1] >> i) & 0x01
        digital_io_status[f"Input {i}"] = ENABLED_STATUS.get(input_bit, "Unknown")

    # Outputs 0–3 (lower 4 bits of the output byte)
    for i in range(4):
        # Extract the i-th bit of the output byte
        output_bit = (data_bytes[2] >> i) & 0x01
        digital_io_status[f"Output {i}"] = ENABLED_STATUS.get(output_bit, "Unknown")

    # Update the status store
    if "Digital IO Status" not in status_store:
        status_store["Digital IO Status"] = {}

    for key, value in digital_io_status.items():
        if status_store["Digital IO Status"].get(key) != value:
            status_store["Digital IO Status"][key] = value

    return status_store


def parse_long_range_drive_status_1(
    data_bytes: list[int],
    status_store: dict[str, dict[str, str]]
) -> dict[str, dict[str, str]]:
    """
    Parse Long Range Drive status 1 from a list of data bytes and update the 
    status store.

    Parameters
    ----------
    data_bytes : list[int]
        A list of integers representing the data bytes to be parsed.
    status_store : dict[str, dict[str, str]]
        A dictionary containing the current status store, which will be updated
        with the parsed Long Range Drive status 1 information.

    Returns
    -------
    dict[str, dict[str, str]]
        The updated status store with the latest Long Range Drive status 1 information.
    """
    # Retrieve bytes from the data list
    byte1 = safe_get(data_bytes, 1)
    byte2 = safe_get(data_bytes, 2)

    # Parse input statuses from the first byte
    parsed_status = {
        f"Input {i}": GLOBAL_ZONE_STATUS.get((byte1 >> (7 - i)) & 0x01, "Unknown")
        for i in range(8)
    }
    # Parse additional input statuses from the second byte
    parsed_status.update({
        f"Input {i + 8}": GLOBAL_ZONE_STATUS.get((byte2 >> (15 - i)) & 0x01, "Unknown")
        for i in range(2)
    })
    # Parse output statuses from the second byte
    parsed_status.update({
        f"Output {i}": GLOBAL_ZONE_STATUS.get((byte2 >> (3 - i)) & 0x01, "Unknown")
        for i in range(4)
    })

    # Define the status key for storing parsed data
    status_key = "LRD Status 1"
    # Initialize the status entry if it doesn't exist
    status_store.setdefault(status_key, {})

    # Update the status store with parsed data if there are changes
    for key, value in parsed_status.items():
        if status_store[status_key].get(key) != value:
            status_store[status_key][key] = value

    return status_store


def parse_long_range_drive_status_2(
    data_bytes: list[int], 
    status_store: dict[str, dict[str, str]]
) -> dict[str, dict[str, str]]:
    """
    Parse Long Range Drive status 2 from a list of data bytes and update the
    status store.

    Parameters
    ----------
    data_bytes : list[int]
        A list of integers representing the data bytes to be parsed.
    status_store : dict[str, dict[str, str]]
        A dictionary containing the current status store, which will be updated
        with the parsed Long Range Drive status 2 information.

    Returns
    -------
    dict[str, dict[str, str]]
        The updated status store with the latest Long Range Drive status 2 
        information.
    """
    bytes_data = [safe_get(data_bytes, i) for i in range(1, 6)]

    parsed_status = {
        **{
            f"Output Overvoltage {i}": GLOBAL_ZONE_STATUS.get((bytes_data[0] >> (7 - i)) & 0x01, "Unknown")
            for i in range(4)
        },
        **{
            f"Output Undervoltage {i}": GLOBAL_ZONE_STATUS.get((bytes_data[1] >> (7 - i)) & 0x01, "Unknown")
            for i in range(4)
        },
        **{
            f"Output Overcurrent {i}": GLOBAL_ZONE_STATUS.get((bytes_data[2] >> (7 - i)) & 0x01, "Unknown")
            for i in range(4)
        },
        **{
            f"Output Undercurrent {i}": GLOBAL_ZONE_STATUS.get((bytes_data[3] >> (7 - i)) & 0x01, "Unknown")
            for i in range(4)
        },
        **{
            f"Serial Comms {i}": GLOBAL_ZONE_STATUS.get((bytes_data[4] >> (7 - i)) & 0x01, "Unknown")
            for i in range(4)
        },
        **{
            f"Drive Signal Comms {i}": GLOBAL_ZONE_STATUS.get((bytes_data[0] >> (3 - i)) & 0x01, "Unknown")
            for i in range(4)
        }
    }

    status_key = "LRD Status 2"
    status_store.setdefault(status_key, {})

    for key, value in parsed_status.items():
        if status_store[status_key].get(key) != value:
            status_store[status_key][key] = value

    return status_store


def parse_locator_failure_update(
    data_bytes: list[int],
    status_store: dict[str, dict[str, str]]
) -> dict[str, dict[str, str]]:
    """
    Parse Locator Failure Update data bytes and update the status store.

    The Locator Failure Update message is used to report the status of Locators
    in the system. The message contains the Locator ID, Failure Type, and Update
    Type.

    Parameters
    ----------
    data_bytes : list[int]
        A list of integers representing the data bytes to be parsed.
    status_store : dict[str, dict[str, str]]
        A dictionary containing the current status store, which will be updated
        with the parsed Locator Failure Update information.

    Returns
    -------
    dict[str, dict[str, str]]
        The updated status store with the latest Locator Failure Update
        information.
    """
    # Extract the Failure Type from the first byte
    failure_type_code = data_bytes[1] & 0b00000111
    # Extract the Update Type from the first byte
    update_type_code = (data_bytes[1] >> 3) & 0b1
    # Extract the Locator ID from the second and third bytes
    locator_id = f"{data_bytes[2]:02X}{data_bytes[3]:02X}"

    # Create a dictionary to store the parsed data
    parsed_data = {
        "locator_id": locator_id,
        "failure_type": LOCATOR_FAILURE_TYPES.get(failure_type_code, f"Unknown ({failure_type_code})"),
        "update_type": LOCATOR_UPDATE_TYPES.get(update_type_code, f"Unknown ({update_type_code})")
    }

    # Initialize the status entry if it doesn't exist
    if "locator_failure_update" not in status_store:
        status_store["locator_failure_update"] = {}

    # Update the status store with the parsed data if there are changes
    for key, value in parsed_data.items():
        if status_store["locator_failure_update"].get(key) != value:
            status_store["locator_failure_update"][key] = value

    return status_store


def parse_message(
    data_bytes: list[int],
    status_store: dict[str, dict[str, str]]
) -> dict[str, dict[str, str]]:
    """
    Parse a list of data bytes and update the status store accordingly.

    This function takes a list of data bytes and a status store as input. It
    uses the parameter code (byte 0) to determine which parser to call, and
    calls the parser function to extract the relevant data from the data bytes
    and update the status store accordingly.

    If no parser is found for the given parameter code, the function returns the
    status store unchanged.

    Parameters
    ----------
    data_bytes : list[int]
        A list of integers representing the data bytes to be parsed.
    status_store : dict[str, dict[str, str]]
        A dictionary containing the current status store, which will be updated
        with the parsed data.

    Returns
    -------
    dict[str, dict[str, str]]
        The updated status store with the latest data.
    """
    # If the data bytes are empty, return the status store unchanged
    if not data_bytes:
        return status_store

    # Extract the parameter code from the first byte of the data bytes
    parameter_code = safe_get(data_bytes, 0)
    # Get the parser function from the PARSERS dictionary
    parser_function = PARSERS.get(parameter_code)

    # If the parser function is found, call it with the data bytes and status
    # store as arguments and return the updated status store
    if parser_function:
        return parser_function(data_bytes, status_store)

    # If no parser is found, return the status store unchanged
    return status_store



PARSERS = {
    0x10: parse_tracking_status,
    0x11: operator_mnid,
    0x12: operator_mnid,
    0x13: operator_mnid,
    0x14: parse_diagnostic_information,
    0x15: parse_can_bus_status,
    0x16: parse_rf_module_status,
    0x17: parse_controller_status,
    0x18: parse_proximity_sensor_status,
    0x19: parse_coil_driver_status,
    0x1A: parse_digital_io_status,
    0x1B: parse_long_range_drive_status_1,
    0x1C: parse_long_range_drive_status_2,
    0x1D: parse_locator_failure_update
}