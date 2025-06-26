#!/home/matrixdesign/IntellizoneVibrationRecorder/.venv/bin/python3

import time
import math
import board
import busio
import adafruit_lsm9ds1
import numpy as np
import matplotlib.pyplot as plt
from ahrs.filters import Madgwick
from mpl_toolkits.mplot3d import Axes3D  # still import for type hints
from typing import cast

# Setup I2C and sensor
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_lsm9ds1.LSM9DS1_I2C(i2c)

# Madgwick filter
madgwick = Madgwick()
q = np.array([1.0, 0.0, 0.0, 0.0])  # initial quaternion

# Magnetometer conversion
UT_TO_GAUSS = 0.01

# Setup 3D plot
plt.ion()
fig = plt.figure(figsize=(8, 8))
ax = cast(Axes3D, fig.add_subplot(111, projection='3d'))

# Define cube vertices (unit cube centered at origin)
cube_definition = [
    np.array([-0.5, -0.5, -0.5]),
    np.array([-0.5, -0.5,  0.5]),
    np.array([-0.5,  0.5, -0.5]),
    np.array([-0.5,  0.5,  0.5]),
    np.array([ 0.5, -0.5, -0.5]),
    np.array([ 0.5, -0.5,  0.5]),
    np.array([ 0.5,  0.5, -0.5]),
    np.array([ 0.5,  0.5,  0.5])
]

def get_cube_lines(cube):
    lines = [
        (cube[0], cube[1]), (cube[0], cube[2]), (cube[0], cube[4]),
        (cube[1], cube[3]), (cube[1], cube[5]),
        (cube[2], cube[3]), (cube[2], cube[6]),
        (cube[3], cube[7]),
        (cube[4], cube[5]), (cube[4], cube[6]),
        (cube[5], cube[7]),
        (cube[6], cube[7])
    ]
    return lines

def rotate_vector(q, v):
    """Rotate vector v by quaternion q"""
    q0, q1, q2, q3 = q
    r = np.array([
        [1 - 2*(q2**2 + q3**2), 2*(q1*q2 - q0*q3), 2*(q1*q3 + q0*q2)],
        [2*(q1*q2 + q0*q3), 1 - 2*(q1**2 + q3**2), 2*(q2*q3 - q0*q1)],
        [2*(q1*q3 - q0*q2), 2*(q2*q3 + q0*q1), 1 - 2*(q1**2 + q2**2)]
    ])
    return np.dot(r, v)

while True:
    try:
        # Read sensors
        gx, gy, gz = sensor.gyro
        ax_, ay_, az_ = sensor.acceleration
        mx, my, mz = sensor.magnetic

        # Convert magnetometer to Gauss
        mx *= UT_TO_GAUSS
        my *= UT_TO_GAUSS
        mz *= UT_TO_GAUSS

        # Convert gyro to rad/s
        gx = math.radians(gx)
        gy = math.radians(gy)
        gz = math.radians(gz)

        # Convert to NumPy arrays for Madgwick
        acc = np.array([ax_, ay_, az_])
        gyr = np.array([gx, gy, gz])
        mag = np.array([mx, my, mz])

        # Apply Madgwick filter
        q = madgwick.updateMARG(q=q, acc=acc, gyr=gyr, mag=mag)

        # Rotate cube vertices
        rotated_cube = [rotate_vector(q, vertex) for vertex in cube_definition]

        # Clear and redraw plot
        ax.cla()
        ax.set_xlim(-1.0, 1.0)
        ax.set_ylim(-1.0, 1.0)
        ax.set_zlim(-1.0, 1.0)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_title("Real-time 3D Orientation")

        for line in get_cube_lines(rotated_cube):
            xs, ys, zs = zip(*line)
            ax.plot(xs, ys, zs, color='b')

        plt.pause(0.001)
        time.sleep(0.05)

    except Exception as e:
        print("Error:", e)
        time.sleep(1)

