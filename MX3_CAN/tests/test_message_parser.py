import pytest

from MX3_CAN.message_parser import parse_tracking_status


def test_parse_tracking_status_valid():
    # Sample valid data_bytes (based on spec)
    data_bytes = [0x10, 0b10010011, 0x01, 0x02, 0x03, 0b10100011]
    status_store = {}

    updated = parse_tracking_status(data_bytes, status_store)

    assert "Tracking_Status" in updated
    tracking = updated["Tracking_Status"]

    assert tracking["Global_Zone_Status"] == "Shutdown/Error"
    assert tracking["Operator_Present"] == "Not Present"
    assert tracking["Closest_Locator_ID"] == "010203"
    assert tracking["Octant_Location"] != "Unknown"
    assert tracking["Screen_Orientation"] != "Unknown"


def test_parse_tracking_status_empty():
    data_bytes = []
    status_store = {}

    updated = parse_tracking_status(data_bytes, status_store)

    # Expect no changes
    assert updated == {}


def test_parse_tracking_status_invalid_length():
    data_bytes = [0x10, 0x01]
    status_store = {}

    with pytest.raises((IndexError, ValueError)):  # Adjust as needed
        parse_tracking_status(data_bytes, status_store)
