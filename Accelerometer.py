#!/home/matrixdesign/IntellizoneVibrationRecorder/.venv/bin/python3

import spidev
import time

# Register addresses (from the datasheet)
CTRL3_C      = 0x12  # Control register: set auto-increment
CTRL1_XL     = 0x10  # Accelerometer control register
OUT_TEMP_L   = 0x20  # Temperature low byte
OUT_TEMP_H   = 0x21  # Temperature high byte
OUTX_L_XL    = 0x28  # Accelerometer X-axis low byte
OUTX_H_XL    = 0x29  # Accelerometer X-axis high byte
OUTY_L_XL    = 0x2A  # Accelerometer Y-axis low byte
OUTY_H_XL    = 0x2B  # Accelerometer Y-axis high byte
OUTZ_L_XL    = 0x2C  # Accelerometer Z-axis low byte
OUTZ_H_XL    = 0x2D  # Accelerometer Z-axis high byte

# Create an SPI object using bus 0, device 1 (/dev/spidev0.1, since CS for LSM6DS3 is on GPIO 7)
spi = spidev.SpiDev()
spi.open(0, 1)
spi.max_speed_hz = 10000000  # Set SPI speed (adjust if necessary)
spi.mode = 0b00            # SPI mode 0

# Helper functions
def write_reg(reg, data):
    # Write 'data' to the specified register
    spi.xfer2([reg, data])
    time.sleep(0.01)

def read_reg(reg, length=1):
    # For a read, set the MSB of the register address (bit7 = 1)
    reg = reg | 0x80
    result = spi.xfer2([reg] + [0x00] * length)
    # The first byte is a dummy; return the rest
    return result[1:]

def twos_complement(val, bits):
    # Compute the 2's complement of int value 'val'
    if val & (1 << (bits - 1)):
        val -= (1 << bits)
    return val

# Sensor initialization
# 1. Set auto-increment on (CTRL3_C: set IF_INC bit, bit2)
write_reg(CTRL3_C, 0x04)
# 2. Configure accelerometer in CTRL1_XL.
# Here 0x50 is chosen as an example:
# - ODR = 104 Hz (bits[7:4] = 0x5) and FS = ±2g (bits[3:2] = 00).
write_reg(CTRL1_XL, 0x50)

# Conversion factors
# For ±2g, sensitivity = 0.061 mg/LSB.
# Convert mg to m/s² (1g = 9.80665 m/s², and 1 mg = 0.001 g)
accel_conv = 0.061e-3 * 9.80665  
# Temperature conversion: Temp (°C) = 25 + (temp_raw / 16)

print("LSM6DS3 initialization complete. Reading data...")

while True:
    # Read temperature (2 bytes)
    temp_l = read_reg(OUT_TEMP_L)[0]
    temp_h = read_reg(OUT_TEMP_H)[0]
    temp_raw = (temp_h << 8) | temp_l
    temp_raw = twos_complement(temp_raw, 16)
    temperature = 25 + (temp_raw / 16.0)

    # Read accelerometer data (6 bytes: X, Y, Z)
    ax_l = read_reg(OUTX_L_XL)[0]
    ax_h = read_reg(OUTX_H_XL)[0]
    ay_l = read_reg(OUTY_L_XL)[0]
    ay_h = read_reg(OUTY_H_XL)[0]
    az_l = read_reg(OUTZ_L_XL)[0]
    az_h = read_reg(OUTZ_H_XL)[0]

    # Combine high and low bytes, using 16-bit 2's complement conversion
    ax_raw = twos_complement((ax_h << 8) | ax_l, 16)
    ay_raw = twos_complement((ay_h << 8) | ay_l, 16)
    az_raw = twos_complement((az_h << 8) | az_l, 16)

    # Convert raw accelerometer data to m/s²
    ax = ax_raw * accel_conv
    ay = ay_raw * accel_conv
    az = az_raw * accel_conv

    # Print values to terminal
    print("Temperature: {:.2f} °C".format(temperature))
    print("Accelerometer: X = {:.3f} m/s², Y = {:.3f} m/s², Z = {:.3f} m/s²".format(ax, ay, az))
    print("-" * 40)
    time.sleep(0.5)
