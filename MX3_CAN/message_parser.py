import logging

from MX3_CAN.config_yaml import *

logger = logging.getLogger(__name__)


def safe_get(data: list[int], index: int, default: int = 0) -> int:
    """
    Safely retrieves an element from a list at the specified index.

    Args:
        data (list[int]): The list from which to retrieve the element.
        index (int): The index of the element to retrieve.
        default (int, optional): The default value to return if the index is out of bounds. Defaults to 0.

    Returns:
        int: The element at the specified index, or the default value if the index is out of bounds.
    """
    # Check if the index is within the bounds of the list
    if index < len(data):
        return data[index]
    # Return the default value if the index is out of bounds
    return default


def parse_tracking_status(
    data_bytes: list[int], status_store: dict[str, dict[str, str]]
) -> dict[str, dict[str, str]]:
    """
    Parses tracking status information from a list of data bytes and updates the status store.

    Args:
        data_bytes (list[int]): The list of bytes containing tracking status information.
        status_store (dict[str, dict[str, str]]): The dictionary to update with parsed status information.

    Returns:
        dict[str, dict[str, str]]: The updated status store with new tracking status information.
    """
    if not data_bytes:
        # Return the unchanged status store if data_bytes is empty
        return status_store

    try:
        # Retrieve specific bytes from the data
        byte1 = safe_get(data_bytes, 1)
        byte2 = safe_get(data_bytes, 2)
        byte3 = safe_get(data_bytes, 3)
        byte4 = safe_get(data_bytes, 4)
        byte5 = safe_get(data_bytes, 5)

        # Extract bit fields from the bytes
        global_zone_status_code = (byte1 >> 6) & 0b11
        operator_presence_code = (byte1 >> 5) & 0b1

        # Construct the Closest Locator ID from bytes 2, 3, and 4
        closest_locator_id = f"{(byte2 << 16 | byte3 << 8 | byte4):06X}"

        # Extract octant location and screen orientation codes from byte 5
        octant_location_code = (byte5 >> 5) & 0b111
        screen_orientation_code = byte5 & 0b11

        # Map codes to human-readable statuses
        parsed_status = {
            "Global_Zone_Status": STATUS_LEVEL.get(global_zone_status_code, "Unknown"),
            "Operator_Present": OPERATOR_PRESENCE.get(
                operator_presence_code, "Unknown"
            ),
            "Closest_Locator_ID": closest_locator_id,
            "Octant_Location": OCTANT_LOCATION.get(octant_location_code, "Unknown"),
            "Screen_Orientation": SCREEN_ORIENTATION.get(
                screen_orientation_code, "Unknown"
            ),
        }

        # Ensure "Tracking Status" exists in the status store
        status_store.setdefault("Tracking_Status", {})

        # Update the status store with parsed values if they have changed
        for key, value in parsed_status.items():
            if status_store["Tracking_Status"].get(key) != value:
                status_store["Tracking_Status"][key] = value

    except Exception as e:
        # Log exception information and the raw data
        logger.exception(f"Error parsing tracking status: {e}")
        logger.debug("Raw data: %s", data_bytes)

    return status_store


def operator_mnid(
    data_bytes: list[int], status_store: dict[str, dict[str, str]]
) -> dict[str, dict[str, str]]:
    """
    Parses Operator MNID information from a list of data bytes and updates the status store.

    Args:
        data_bytes (list[int]): The list of bytes containing MNID information.
        status_store (dict[str, dict[str, str]]): The dictionary to update with parsed MNID information.

    Returns:
        dict[str, dict[str, str]]: The updated status store with new MNID information.
    """
    if not data_bytes:
        # Return the unchanged status store if data_bytes is empty
        return status_store

    try:
        # Define keys for MNID storage
        mnid_keys = ["OperatorMNID_1", "OperatorMNID_2", "OperatorMNID_3"]

        # Parse MNID from the data bytes
        parsed_mnid = {
            mnid_keys[
                i
            ]: f"{safe_get(data_bytes, 2 * i + 2):02X}{safe_get(data_bytes, 2 * i + 3):02X}"
            for i in range(3)
        }

        # Ensure "OperatorMNID" exists in the status store
        status_store.setdefault("Operator_MNID", {})

        # Update the status store with parsed MNID values if they have changed
        for key, value in parsed_mnid.items():
            if status_store["Operator_MNID"].get(key) != value:
                status_store["Operator_MNID"][key] = value

    except Exception as e:
        # Log exception information and the raw data
        logger.exception("Error parsing Operator MNID: %s", e)
        logger.debug("Raw data: %s", data_bytes)

    return status_store


def parse_diagnostic_information(
    data_bytes: list[int], status_store: dict[str, dict[str, str]]
) -> dict[str, dict[str, str]]:
    """
    Parses diagnostic information from a list of data bytes and updates the status store.

    Args:
        data_bytes (list[int]): The list of bytes containing diagnostic information.
        status_store (dict[str, dict[str, str]]): The dictionary to update with parsed diagnostic information.

    Returns:
        dict[str, dict[str, str]]: The updated status store with new diagnostic information.
    """
    if not data_bytes:
        # Return the unchanged status store if data_bytes is empty
        return status_store

    diagnostic_info = {}

    try:
        # Get the first two bytes of the data
        byte_1 = safe_get(data_bytes, 1)
        byte_2 = safe_get(data_bytes, 2)

        # Parse the diagnostic information from the first two bytes
        diagnostic_info["Global_System_Status"] = GLOBAL_ZONE_STATUS.get(
            (byte_1 >> 6) & 0b11, "Unknown"
        )
        diagnostic_info["Driver_0_Status"] = GLOBAL_ZONE_STATUS.get(
            (byte_2 >> 6) & 0b11, "Unknown"
        )
        diagnostic_info["Driver_1_Status"] = GLOBAL_ZONE_STATUS.get(
            (byte_2 >> 4) & 0b11, "Unknown"
        )
        diagnostic_info["Driver_2_Status"] = GLOBAL_ZONE_STATUS.get(
            (byte_2 >> 2) & 0b11, "Unknown"
        )
        diagnostic_info["Driver_3_Status"] = GLOBAL_ZONE_STATUS.get(
            byte_2 & 0b11, "Unknown"
        )

        # Ensure "Diagnostic Information" exists in the status store
        status_store.setdefault("Diagnostic_Information", {})

        # Update the status store with parsed diagnostic information if it has changed
        for key, value in diagnostic_info.items():
            if status_store["Diagnostic_Information"].get(key) != value:
                status_store["Diagnostic_Information"][key] = value

    except Exception as e:
        # Log exception information and the raw data
        logger.exception("Error parsing diagnostic information: %s", e)
        logger.debug("Raw data: %s", data_bytes)

    return status_store


def parse_can_bus_status(
    data_bytes: list[int], status_store: dict[str, dict[str, str]]
) -> dict[str, dict[str, str]]:
    """
    Parses CAN bus status information from a list of data bytes and updates the status store.

    Args:
        data_bytes (list[int]): The list of bytes containing CAN bus status information.
        status_store (dict[str, dict[str, str]]): The dictionary to update with parsed CAN bus status information.

    Returns:
        dict[str, dict[str, str]]: The updated status store with new CAN bus status information.
    """
    if not data_bytes:
        # Return the unchanged status store if data_bytes is empty
        return status_store

    try:
        # Initialize a dictionary to store the parsed CAN bus status information
        can_bus_status = {}

        # Get the first two bytes of the data
        byte_1 = safe_get(data_bytes, 1)
        byte_2 = safe_get(data_bytes, 2)

        # Parse the CAN bus status information from the first two bytes
        can_bus_status["Vortex_CAN_Bus_Status"] = GLOBAL_ZONE_STATUS.get(
            byte_1, "Unknown"
        )
        can_bus_status["AVR_CAN_Bus_Status"] = GLOBAL_ZONE_STATUS.get(byte_2, "Unknown")

        # Ensure "CANBus Status" exists in the status store
        status_store.setdefault("CANBus_Status", {})

        # Update the status store with parsed CAN bus status information if it has changed
        for key, value in can_bus_status.items():
            if status_store["CANBus_Status"].get(key) != value:
                status_store["CANBus_Status"][key] = value

    except Exception as e:
        # Log exception information and the raw data
        logger.exception("Error parsing <Message Type>: %s", e)
        logger.debug("Raw data: %s", data_bytes)

    return status_store


def parse_rf_module_status(
    data_bytes: list[int], status_store: dict[str, dict[str, str]]
) -> dict[str, dict[str, str]]:
    """
    Parses the status of the RF module from a list of data bytes and updates the status store.

    Args:
        data_bytes (list[int]): The list of bytes containing the status of the RF module.
        status_store (dict[str, dict[str, str]]): The dictionary to update with the parsed status information.

    Returns:
        dict[str, dict[str, str]]: The updated status store with the new status information.
    """
    if not data_bytes:
        return status_store

    parsed_status = {}

    try:
        # Get the serial communication status
        parsed_status["Serial_Comms_Status"] = GLOBAL_ZONE_STATUS.get(
            safe_get(data_bytes, 1), "Unknown"
        )

        # Get the M-NET connection status
        parsed_status["Mnet_Connection_Status"] = GLOBAL_ZONE_STATUS.get(
            safe_get(data_bytes, 2), "Unknown"
        )

        # Get the wireless AVR error code status
        parsed_status["Wireless_Avr_Error_Code_Status"] = GLOBAL_ZONE_STATUS.get(
            safe_get(data_bytes, 3), "Unknown"
        )

        # Update the status store with the parsed status information
        status_key = "RF_Module_Status"

        # Initialize the status entry if it doesn't exist
        status_store.setdefault(status_key, {})

        for key, value in parsed_status.items():
            if status_store[status_key].get(key) != value:
                status_store[status_key][key] = value

    except Exception as e:
        logger.exception("Error parsing <Message Type>: %s", e)
        logger.debug("Raw data: %s", data_bytes)

    return status_store


def parse_controller_status(
    data_bytes: list[int], status_store: dict[str, dict[str, str]]
) -> dict[str, dict[str, str]]:
    """
    Parses controller status information from a list of data bytes and updates the status store.

    Args:
        data_bytes (list[int]): The list of bytes containing the status of the controller.
        status_store (dict[str, dict[str, str]]): The dictionary to update with parsed status information.

    Returns:
        dict[str, dict[str, str]]: The updated status store with the new status information.
    """
    if not data_bytes:
        return status_store

    controller_status = {}

    try:
        byte1 = safe_get(data_bytes, 1)
        byte2 = safe_get(data_bytes, 2)
        byte3 = safe_get(data_bytes, 3)
        byte4 = safe_get(data_bytes, 4)

        # Controller Version Status (0x00 - 0xFF)
        controller_status["Controller_Version_Status"] = GLOBAL_ZONE_STATUS.get(
            (byte1 >> 6) & 0b11, "Unknown"
        )

        # Vortex Board Version Status (0x00 - 0xFF)
        controller_status["Vortex_Board_Version_Status"] = GLOBAL_ZONE_STATUS.get(
            (byte1 >> 2) & 0b11, "Unknown"
        )

        # KeyLok Authentication Status (0x00 - 0xFF)
        controller_status["KeyLok_Authentication_Status"] = GLOBAL_ZONE_STATUS.get(
            (byte2 >> 6) & 0b11, "Unknown"
        )

        # Soft PLC Comms Status (0x00 - 0xFF)
        controller_status["Soft_PLC_Comms_Status"] = GLOBAL_ZONE_STATUS.get(
            (byte2 >> 2) & 0b11, "Unknown"
        )

        # CAN Serial Number Status (0x00 - 0xFF)
        controller_status["CAN_Serial_Number_Status"] = GLOBAL_ZONE_STATUS.get(
            (byte3 >> 6) & 0b11, "Unknown"
        )

        # MML RF Signal Detection Status (0x00 - 0xFF)
        controller_status["MML_RF_Signal_Detection_Status"] = GLOBAL_ZONE_STATUS.get(
            (byte3 >> 2) & 0b11, "Unknown"
        )

        # MML Mag Signal Detection Status (0x00 - 0xFF)
        controller_status["MML_Mag_Signal_Detection_Driver_0_Status"] = (
            GLOBAL_ZONE_STATUS.get((byte4 >> 6) & 0b11, "Unknown")
        )
        controller_status["MML_Mag_Signal_Detection_Driver_1_Status"] = (
            GLOBAL_ZONE_STATUS.get((byte4 >> 4) & 0b11, "Unknown")
        )
        controller_status["MML_Mag_Signal_Detection_Driver_2_Status"] = (
            GLOBAL_ZONE_STATUS.get((byte4 >> 2) & 0b11, "Unknown")
        )
        controller_status["MML_Mag_Signal_Detection_Driver_3_Status"] = (
            GLOBAL_ZONE_STATUS.get(byte4 & 0b11, "Unknown")
        )

        # Update the status store with the parsed status information
        status_store.setdefault("Controller_Status", {})

        for key, value in controller_status.items():
            if status_store["Controller_Status"].get(key) != value:
                status_store["Controller_Status"][key] = value

    except Exception as e:
        logger.exception("Error parsing <Message Type>: %s", e)
        logger.debug("Raw data: %s", data_bytes)

    return status_store


def parse_proximity_sensor_status(
    data_bytes: list[int], status_store: dict[str, dict[str, str]]
) -> dict[str, dict[str, str]]:
    """
    Parses proximity sensor status information from a list of data bytes
    and updates the status store.

    Args:
        data_bytes (list[int]): The list of bytes containing proximity sensor status information.
        status_store (dict[str, dict[str, str]]): The dictionary to update with parsed status information.

    Returns:
        dict[str, dict[str, str]]: The updated status store with new proximity sensor status information.
    """
    if not data_bytes:
        # Return the unchanged status store if data_bytes is empty
        return status_store

    parsed_status = {}

    try:
        # Retrieve specific bytes from the data
        byte_1 = safe_get(data_bytes, 1)
        byte_2 = safe_get(data_bytes, 2)
        byte_3 = safe_get(data_bytes, 3)

        # Parse proximity sensor status information from the bytes
        parsed_status = {
            "Sync_Rate": PROXIMITY_SYNC_RATE.get((byte_1 >> 4) & 0b1111, "Unknown"),
            "Locator_Test_Status": GLOBAL_ZONE_STATUS.get(
                (byte_1 >> 2) & 0b11, "Unknown"
            ),
            "Sync_Rate_Status": GLOBAL_ZONE_STATUS.get(byte_1 & 0b11, "Unknown"),
            "Locator_Wave_Set_Status": GLOBAL_ZONE_STATUS.get(
                (byte_2 >> 6) & 0b11, "Unknown"
            ),
            "Locator_Battery_Voltage_Status": GLOBAL_ZONE_STATUS.get(
                (byte_2 >> 2) & 0b11, "Unknown"
            ),
            "Locator_No_FPGA_Int_Status": GLOBAL_ZONE_STATUS.get(
                (byte_3 >> 6) & 0b11, "Unknown"
            ),
            "Locator_Driver_Distance_Status": GLOBAL_ZONE_STATUS.get(
                (byte_3 >> 2) & 0b11, "Unknown"
            ),
        }

        # Define the status key for storing parsed data
        status_key = "Proximity_SensorStatus"
        # Initialize the status entry if it doesn't exist
        status_store.setdefault(status_key, {})

        # Update the status store with parsed data if there are changes
        for key, value in parsed_status.items():
            if status_store[status_key].get(key) != value:
                status_store[status_key][key] = value
    except Exception as e:
        # Log exception information and the raw data
        logger.exception("Error parsing <Message Type>: %s", e)
        logger.debug("Raw data: %s", data_bytes)

    return status_store


def parse_coil_driver_status(
    data_bytes: list[int], status_store: dict[str, dict[str, str]]
) -> dict[str, dict[str, str]]:
    """
    Parses coil driver status information from a list of data bytes
    and updates the status store.

    Args:
        data_bytes (list[int]): The list of bytes containing coil driver status information.
        status_store (dict[str, dict[str, str]]): The dictionary to update with parsed status information.

    Returns:
        dict[str, dict[str, str]]: The updated status store with new coil driver status information.
    """
    if not data_bytes:
        return status_store

    parsed_status = {}
    try:
        # Extract coil driver status for each driver (4 bytes)
        for byte_index, byte_name in enumerate(
            ["Serial_Comms", "Signal_Open", "Signal_Short", "Power_Open", "Power_Short"]
        ):
            parsed_status.update(
                {
                    # Shift the byte value by 6 - i * 2 to get the status for the i-th driver
                    f"{byte_name.title()} Driver {i}": GLOBAL_ZONE_STATUS.get(
                        (safe_get(data_bytes, byte_index + 1) >> (6 - i * 2)) & 0b11,
                        "Unknown",
                    )
                    for i in range(4)
                }
            )

        # Extract additional coil driver status
        parsed_status.update(
            {
                "Driver_Enable_0": ENABLED_STATUS.get(
                    (safe_get(data_bytes, 6) >> 7) & 0b01, "Unknown"
                ),
                "Driver_Enable_1": ENABLED_STATUS.get(
                    (safe_get(data_bytes, 6) >> 5) & 0b01, "Unknown"
                ),
                "Driver_Enable_2": ENABLED_STATUS.get(
                    (safe_get(data_bytes, 6) >> 3) & 0b01, "Unknown"
                ),
                "Driver_Enable_3": ENABLED_STATUS.get(
                    (safe_get(data_bytes, 6) >> 1) & 0b01, "Unknown"
                ),
                "72V_Supply_Status": GLOBAL_ZONE_STATUS.get(
                    (safe_get(data_bytes, 7) >> 2) & 0b11, "Unknown"
                ),
            }
        )

        # Update the status store
        status_key = "Coil_Driver_Status"
        if status_key not in status_store:
            status_store[status_key] = {}

        for key, value in parsed_status.items():
            if status_store[status_key].get(key) != value:
                status_store[status_key][key] = value
    except Exception as e:
        logger.exception("Error parsing <Message Type>: %s", e)
        logger.debug("Raw data: %s", data_bytes)

    return status_store


def parse_digital_io_status(
    data_bytes: list[int], status_store: dict[str, dict[str, str]]
) -> dict[str, dict[str, str]]:
    """
    Parses digital IO status information from a list of data bytes
    and updates the status store.

    Args:
        data_bytes (list[int]): The list of bytes containing digital IO status information.
        status_store (dict[str, dict[str, str]]): The dictionary to update with parsed status information.

    Returns:
        dict[str, dict[str, str]]: The updated status store with new digital IO status information.
    """
    if not data_bytes:
        return status_store

    digital_io_status = {}
    try:
        # Retrieve bytes from the data list
        byte1 = safe_get(data_bytes, 1)
        byte2 = safe_get(data_bytes, 2)

        # Inputs 0–9 (first 10 bits of a 2-byte field)
        for i in range(10):
            # Extract the i-th bit of the input byte
            input_bit = (byte1 >> i) & 0x01
            digital_io_status[f"Input_{i}"] = ENABLED_STATUS.get(input_bit, "Unknown")

        # Outputs 0–3 (lower 4 bits of the output byte)
        for i in range(4):
            # Extract the i-th bit of the output byte
            output_bit = (byte2 >> i) & 0x01
            digital_io_status[f"Output_{i}"] = ENABLED_STATUS.get(output_bit, "Unknown")

        # Update the status store
        if "Digital_IO_Status" not in status_store:
            status_store["Digital_IO_Status"] = {}

        for key, value in digital_io_status.items():
            if status_store["Digital_IO_Status"].get(key) != value:
                status_store["Digital_IO_Status"][key] = value
    except Exception as e:
        logger.exception("Error parsing <Message Type>: %s", e)
        logger.debug("Raw data: %s", data_bytes)
    return status_store


def parse_long_range_drive_status_1(
    data_bytes: list[int], status_store: dict[str, dict[str, str]]
) -> dict[str, dict[str, str]]:
    """
    Parses long range drive status 1 information from a list of data bytes
    and updates the status store.

    Args:
        data_bytes (list[int]): The list of bytes containing long range drive status 1 information.
        status_store (dict[str, dict[str, str]]): The dictionary to update with parsed status information.

    Returns:
        dict[str, dict[str, str]]: The updated status store with new long range drive status 1 information.
    """
    if not data_bytes:
        return status_store

    parsed_status = {}
    try:
        # Retrieve bytes from the data list
        byte1 = safe_get(data_bytes, 1)
        byte2 = safe_get(data_bytes, 2)

        # Parse input statuses from the first byte
        parsed_status = {
            # Parse 8 input statuses from the first byte
            f"Input {i}": GLOBAL_ZONE_STATUS.get((byte1 >> (7 - i)) & 0x01, "Unknown")
            for i in range(8)
        }
        # Parse additional input statuses from the second byte
        parsed_status.update(
            {
                # Parse 2 additional input statuses from the second byte
                f"Input {i + 8}": GLOBAL_ZONE_STATUS.get(
                    (byte2 >> (15 - i)) & 0x01, "Unknown"
                )
                for i in range(2)
            }
        )
        # Parse output statuses from the second byte
        parsed_status.update(
            {
                # Parse 4 output statuses from the second byte
                f"Output {i}": GLOBAL_ZONE_STATUS.get(
                    (byte2 >> (3 - i)) & 0x01, "Unknown"
                )
                for i in range(4)
            }
        )

        # Define the status key for storing parsed data
        status_key = "LRD_Status_1"
        # Initialize the status entry if it doesn't exist
        status_store.setdefault(status_key, {})

        # Update the status store with parsed data if there are changes
        for key, value in parsed_status.items():
            if status_store[status_key].get(key) != value:
                status_store[status_key][key] = value
    except Exception as e:
        logger.exception("Error parsing <Message Type>: %s", e)
        logger.debug("Raw data: %s", data_bytes)
    return status_store


def parse_long_range_drive_status_2(
    data_bytes: list[int], status_store: dict[str, dict[str, str]]
) -> dict[str, dict[str, str]]:
    """
    Parses long range drive status 2 information from a list of data bytes
    and updates the status store.

    Args:
        data_bytes (list[int]): The list of bytes containing long range drive status 2 information.
        status_store (dict[str, dict[str, str]]): The dictionary to update with parsed status information.

    Returns:
        dict[str, dict[str, str]]: The updated status store with new long range drive status 2 information.
    """
    if not data_bytes:
        return status_store

    parsed_status = {}
    try:
        # Retrieve bytes from the data list
        bytes_data = [safe_get(data_bytes, i) for i in range(1, 6)]

        # Parse error statuses from the first byte
        parsed_status = {
            **{
                # Parse 4 output overvoltage statuses from the first byte
                f"Output_Overvoltage {i}": GLOBAL_ZONE_STATUS.get(
                    (bytes_data[0] >> (7 - i)) & 0x01, "Unknown"
                )
                for i in range(4)
            },
            **{
                # Parse 4 output undervoltage statuses from the second byte
                f"Output_Undervoltage {i}": GLOBAL_ZONE_STATUS.get(
                    (bytes_data[1] >> (7 - i)) & 0x01, "Unknown"
                )
                for i in range(4)
            },
            **{
                # Parse 4 output overcurrent statuses from the third byte
                f"Output_Overcurrent {i}": GLOBAL_ZONE_STATUS.get(
                    (bytes_data[2] >> (7 - i)) & 0x01, "Unknown"
                )
                for i in range(4)
            },
            **{
                # Parse 4 output undercurrent statuses from the fourth byte
                f"Output_Undercurrent {i}": GLOBAL_ZONE_STATUS.get(
                    (bytes_data[3] >> (7 - i)) & 0x01, "Unknown"
                )
                for i in range(4)
            },
            **{
                # Parse 4 serial comms statuses from the fifth byte
                f"Serial_Comms {i}": GLOBAL_ZONE_STATUS.get(
                    (bytes_data[4] >> (7 - i)) & 0x01, "Unknown"
                )
                for i in range(4)
            },
            **{
                # Parse 4 drive signal comms statuses from the first byte
                f"Drive_Signal_Comms {i}": GLOBAL_ZONE_STATUS.get(
                    (bytes_data[0] >> (3 - i)) & 0x01, "Unknown"
                )
                for i in range(4)
            },
        }

        # Define the status key for storing parsed data
        status_key = "LRD_Status_2"
        # Initialize the status entry if it doesn't exist
        status_store.setdefault(status_key, {})

        # Update the status store with parsed data if there are changes
        for key, value in parsed_status.items():
            if status_store[status_key].get(key) != value:
                status_store[status_key][key] = value
    except Exception as e:
        logger.exception("Error parsing <Message Type>: %s", e)
        logger.debug("Raw data: %s", data_bytes)
    return status_store


def parse_locator_failure_update(
    data_bytes: list[int], status_store: dict[str, dict[str, str]]
) -> dict[str, dict[str, str]]:
    """
    Parse the Locator Failure Update message and update the status store with the parsed data.

    Parameters:
    data_bytes (list[int]): The list of bytes containing Locator Failure Update information.
    status_store (dict[str, dict[str, str]]): The dictionary to update with parsed status information.

    Returns:
    dict[str, dict[str, str]]: The updated status store with new Locator Failure Update information.
    """
    if not data_bytes:
        return status_store

    parsed_data = {}

    try:
        # Extract the Failure Type from the first byte
        failure_type_code = safe_get(data_bytes, 1) & 0b00000111
        # Extract the Update Type from the first byte
        update_type_code = (safe_get(data_bytes, 1) >> 3) & 0b1
        # Extract the Locator ID from the second and third bytes
        locator_id = f"{safe_get(data_bytes, 2):02X}{safe_get(data_bytes, 3):02X}"

        # Create a dictionary to store the parsed data
        parsed_data = {
            "Locator_ID": locator_id,
            "Failure_Type": LOCATOR_FAILURE_TYPES.get(
                failure_type_code, f"Unknown ({failure_type_code})"
            ),
            "Update_Type": LOCATOR_UPDATE_TYPES.get(
                update_type_code, f"Unknown ({update_type_code})"
            ),
        }

        # Initialize the status entry if it doesn't exist
        if "Locator_Failure_Update" not in status_store:
            status_store["Locator_Failure_Update"] = {}

        # Update the status store with the parsed data if there are changes
        for key, value in parsed_data.items():
            if status_store["Locator_Failure_Update"].get(key) != value:
                status_store["Locator_Failure_Update"][key] = value
    except Exception as e:
        logger.exception("Error parsing <Message Type>: %s", e)
        logger.debug("Raw data: %s", data_bytes)
    return status_store


def parse_message(
    data_bytes: list[int], status_store: dict[str, dict[str, str]]
) -> dict[str, dict[str, str]]:
    """
    Parse a list of data bytes into a dictionary of parsed status information.

    Args:
        data_bytes (list[int]): The list of bytes containing the status information
        status_store (dict[str, dict[str, str]]): The dictionary to update with parsed status information

    Returns:
        dict[str, dict[str, str]]: The updated status store with new status information
    """
    # If the data bytes are empty, return the status store unchanged
    if not data_bytes:
        return status_store
    try:
        # Extract the parameter code from the first byte of the data bytes
        parameter_code = safe_get(data_bytes, 0)
        # Get the parser function from the PARSERS dictionary
        parser_function = PARSERS.get(parameter_code)

        # If the parser function is found, call it with the data bytes and status
        # store as arguments and return the updated status store
        if parser_function:
            return parser_function(data_bytes, status_store)

    except Exception as e:
        logger.exception("Error parsing <Message Type>: %s", e)
        logger.debug("Raw data: %s", data_bytes)
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
    0x1D: parse_locator_failure_update,
}
