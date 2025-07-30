#!/home/matrixdesign/IntellizoneVibrationRecorder/.venv/bin/python3
import logging
import time

from config_yaml import LSM9DS1_CONFIG
from devices.accelerometer import Accelerometer
from devices.gyroscope import Gyroscope
from devices.lsm9ds1_device import LSM9DS1Device
from devices.magnetometer import Magnetometer
from devices.temperature import TemperatureSensor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def main():
    # Load I2C configuration
    i2c_cfg = LSM9DS1_CONFIG["I2C"]

    # Initialize I2C device with both addresses
    device = LSM9DS1Device(
        i2c_bus=i2c_cfg["bus"],
        accel_gyro_address=i2c_cfg["accel_gyro_address"],
        magnetometer_address=i2c_cfg["magnetometer_address"],
    )

    # Set up sensors
    temp_sensor = TemperatureSensor(device)
    accel = Accelerometer(device)
    mag = Magnetometer(device)
    gyro = Gyroscope(device)

    gyro.configure()
    accel.configure()
    mag.configure()

    logger.info(
        "Reading LSM9DS1 accelerometer, gyroscope, magnetometer, and temperature..."
    )
    try:
        while True:
            temperature_c = temp_sensor.read_temperature_celsius()
            gyro_dps = {
                axis: round(val, 3)
                for axis, val in gyro.read_angular_velocity_dps().items()
            }
            mg_values = {
                axis: round(val, 3) for axis, val in accel.read_acceleration().items()
            }
            mag_field = {
                axis: round(val, 3)
                for axis, val in mag.read_magnetic_field_uT().items()
            }

            logger.info(
                f"Temp [°C]: {temperature_c:.2f} | "
                f"Accel: x={mg_values['x']}mg y={mg_values['y']}mg z={mg_values['z']}mg | "
                f"Gyro: x={gyro_dps['x']}dps y={gyro_dps['y']}dps z={gyro_dps['z']}dps | "
                f"Mag: x={mag_field['x']}µT y={mag_field['y']}µT z={mag_field['z']}µT"
            )

            time.sleep(0.5)
    except KeyboardInterrupt:
        logger.info("Exiting on user request.")
    except Exception as e:
        logger.exception(f"Unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
