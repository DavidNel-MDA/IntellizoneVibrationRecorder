#!/home/matrixdesign/IntellizoneVibrationRecorder/.venv/bin/python3

import smbus2
import time
import struct

from devices.accelerometer import Accelerometer

acc = Accelerometer()
acc.initialize()

x, y, z = acc.read_raw()
print(f"Raw Accel (X, Y, Z): {x}, {y}, {z}")