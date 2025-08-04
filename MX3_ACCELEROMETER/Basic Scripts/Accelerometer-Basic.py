#!/home/matrixdesign/IntellizoneVibrationRecorder/.venv/bin/python3

import time

import adafruit_lsm9ds1
import board
import busio

# I2C setup
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_lsm9ds1.LSM9DS1_I2C(i2c)

# Conversion factors from datasheet
G_TO_MS2 = 9.80665  # convert g to m/s²
UT_TO_GAUSS = 0.01  # uTesla to Gauss

while True:
    accel_x, accel_y, accel_z = sensor.acceleration  # m/s² already
    mag_x, mag_y, mag_z = sensor.magnetic  # in uTesla
    temp_c = sensor.temperature  # °C

    # Convert magnetic field to Gauss
    mag_x_gauss = mag_x * UT_TO_GAUSS
    mag_y_gauss = mag_y * UT_TO_GAUSS
    mag_z_gauss = mag_z * UT_TO_GAUSS

    print(
        "Acceleration (m/s²): X={:.2f} Y={:.2f} Z={:.2f}".format(
            accel_x, accel_y, accel_z
        )
    )
    print(
        "Magnetic field (Gauss): X={:.2f} Y={:.2f} Z={:.2f}".format(
            mag_x_gauss, mag_y_gauss, mag_z_gauss
        )
    )
    print("Temperature (°C): {:.2f}".format(temp_c))
    print("-" * 40)
    time.sleep(1)
