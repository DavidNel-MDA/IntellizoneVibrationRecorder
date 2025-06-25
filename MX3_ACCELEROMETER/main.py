#!/home/matrixdesign/IntellizoneVibrationRecorder/.venv/bin/python3

import smbus2
import time
import struct

from config_yaml import ACCELEROMETER_ADDRESS, ACCELEROMETER_GYROSCOPE_REGISTER, MAGNETOMETER_REGISTER


# Open I2C bus (usually 1 on Raspberry Pi)
bus = smbus2.SMBus(1)

# Confirm connection
who_am_i = bus.read_byte_data(
    ACCELEROMETER_ADDRESS, 
    ACCELEROMETER_GYROSCOPE_REGISTER["Who_Am_I"]
    )
print(f"WHO_AM_I register: 0x{who_am_i:X} (expected 0x68)")

# Initialize accelerometer: 952 Hz, ±2g, bandwidth auto
bus.write_byte_data(
    ACCELEROMETER_ADDRESS, 
    ACCELEROMETER_GYROSCOPE_REGISTER["Accelerometer_Control_6"], 
    0b01100000
    )

# Initialize gyroscope: 952 Hz, 245 dps
bus.write_byte_data(
    ACCELEROMETER_ADDRESS, 
    ACCELEROMETER_GYROSCOPE_REGISTER["Gyroscope_Control_1"], 
    0b01100000
    )

# Read loop
while True:
    # Read 6 bytes from OUT_X_L_XL (accelerometer X,Y,Z)
    data = bus.read_i2c_block_data(
        ACCELEROMETER_ADDRESS, 
        ACCELEROMETER_GYROSCOPE_REGISTER["Accelerometer_X_Low"] | 0x80, 
        6
        )

    # Unpack little endian 16-bit signed values
    x, y, z = struct.unpack('<hhh', bytes(data))

    # Convert to m/s² (assuming ±2g scale, 0.061 mg/LSB)
    factor = 0.061 * 9.80665 / 1000  # mg to m/s²
    ax = x * factor
    ay = y * factor
    az = z * factor

    print(f"Accel: X={ax:.2f} m/s² Y={ay:.2f} m/s² Z={az:.2f} m/s²")

    time.sleep(0.1)