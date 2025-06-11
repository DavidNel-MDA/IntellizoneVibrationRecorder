from bidict import bidict

DISCOVERY_TIMEOUT= 300.0

# Configuration parameters
UID = [0x45, 0x2F, 0xA7, 0xA2]                  # Replace with real UID
BITRATE = 125000

MODULE_TYPE = bidict({
    "Controller":	    0x3,
    "Driver":           0x6,
    "MML":              0x9,
    "Tracker":          0xA,
    "Status_Screen":    0xC,
    "Reserved":         0xF,
})


# Controller Message Types
CONTROLLER_MESSAGE_TYPE = bidict({
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
})


GLOBAL_ZONE_STATUS = {
    0b00: "Safe/Normal",
    0b01: "Warning",
    0b10: "Shutdown/Error",
    0b11: "Reserved"
}

OCTANT_LOCATION = {
    0b000: "0-45 Octant",
    0b001: "45-90 Octant",
    0b010: "90-135 Octant",
    0b011: "135-180 Octant",
    0b100: "180-225 Octant",
    0b101: "225-270 Octant",
    0b110: "270-315 Octant",
    0b111: "315-360 Octant"
}

SCREEN_ORIENTATION = {
    0b00: "Front",
    0b01: "Right",
    0b10: "Back",
    0b11: "Left"
}

STATUS_LEVEL = {
    0b00: "Safe/Normal",
    0b01: "Warning",
    0b10: "Shutdown/Error",
    0b11: "Reserved"
}


OPERATOR_PRESENCE = {
    0: "Not Present",
    1: "Present"
}

SYNC_RATE = {
    0x00: "20 ms",
    0x01: "30 ms",
    0x02: "40 ms",
    0x03: "50 ms",
    0x04: "60 ms",
    0x05: "70 ms",
    0x06: "80 ms",
    0x07: "90 ms",
    0x08: "100 ms",
}


PROXIMITY_SYNC_RATE = {
    0b0000: "100ms",
    0b0001: "200ms",
    0b0010: "300ms",
    0b0011: "400ms",
    0b0100: "500ms",
    0b0101: "600ms",
    0b0110: "700ms",
    0b0111: "800ms",
    0b1000: "900ms"
}



ENABLED_STATUS = {
    0b0: "Disabled",
    0b1: "Enabled"
}


LOCATOR_FAILURE_TYPES = {
    0b000: "Test Status",
    0b001: "Wave Set",
    0b010: "Battery Voltage",
    0b011: "No FPGA Int",
    0b100: "Driver Dist Diff",
    0b101: "Reserved",
    0b110: "Reserved",
    0b111: "Reserved"
}

LOCATOR_UPDATE_TYPES = {
    0: "Remove",
    1: "Add"
}