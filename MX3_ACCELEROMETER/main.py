#!/home/matrixdesign/IntellizoneVibrationRecorder/.venv/bin/python3
from devices.lsm9ds1_device import LSM9DS1Device
from devices.accelerometer import Accelerometer
from devices.magnetometer import Magnetometer
from devices.gyroscope import Gyroscope
from devices.temperature import TemperatureSensor
from config_yaml import LSM9DS1_CONFIG
import time

def main():
    # Load I2C configuration
    i2c_cfg = LSM9DS1_CONFIG["I2C"]

    # Initialize I2C device with both addresses
    device = LSM9DS1Device(
        i2c_bus=i2c_cfg["bus"],
        accel_gyro_address=i2c_cfg["accel_gyro_address"],
        magnetometer_address=i2c_cfg["magnetometer_address"]
    )

    # Set up sensors
    temp_sensor = TemperatureSensor(device)
    accel = Accelerometer(device)
    mag = Magnetometer(device)
    gyro = Gyroscope(device)
    
    gyro.configure()
    accel.configure()
    mag.configure()

    print("Reading LSM9DS1 accelerometer and magnetometer...")
    while True:
        temperature_c = temp_sensor.read_temperature_celsius()
        gyro_data = gyro.read_angular_velocity()
        acc = accel.read_acceleration()
        mag_field = mag.read_magnetic_field()

        print(
            f"Temp [°C]: {temperature_c:.2f} | "
            f"Accel: x={acc['x']} y={acc['y']} z={acc['z']} | "
            f"Gyro: x={gyro_data['x']} y={gyro_data['y']} z={gyro_data['z']} | "
            f"Mag: x={mag_field['x']} y={mag_field['y']} z={mag_field['z']}"
        )

        time.sleep(0.5)

if __name__ == "__main__":
    main()
