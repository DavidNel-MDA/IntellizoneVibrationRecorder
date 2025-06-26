from devices.lsm9ds1_device import LSM9DS1Device
from config_yaml import (
    ACCELEROMETER_ADDRESS,
    ACCELEROMETER_GYROSCOPE_REGISTER,
)
from settings import CTRL6_VALUE

class Accelerometer(LSM9DS1Device):
    def __init__(self, bus_num=1):
        super().__init__(bus_num, ACCELEROMETER_ADDRESS, ACCELEROMETER_GYROSCOPE_REGISTER)

    def initialize(self):
        self.write_register("Accelerometer_Control_6", CTRL6_VALUE)

    def read_raw(self):
        data = self.read_block("Accelerometer_X_Low", 6)
        x = self._combine_bytes(data[1], data[0])
        y = self._combine_bytes(data[3], data[2])
        z = self._combine_bytes(data[5], data[4])
        return x, y, z
