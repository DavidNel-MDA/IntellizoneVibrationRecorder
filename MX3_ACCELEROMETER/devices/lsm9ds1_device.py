import smbus2

class LSM9DS1Device:
    def __init__(self, i2c_bus: int, accel_gyro_address: int, magnetometer_address: int):
        self.bus = smbus2.SMBus(i2c_bus)
        self.addr_ag = accel_gyro_address
        self.addr_mag = magnetometer_address

    def write_byte(self, addr_type: str, reg: int, value: int):
        addr = self.addr_ag if addr_type == "AG" else self.addr_mag
        self.bus.write_byte_data(addr, reg, value)

    def read_bytes(self, addr_type: str, start_reg: int, length: int) -> list[int]:
        addr = self.addr_ag if addr_type == "AG" else self.addr_mag
        return self.bus.read_i2c_block_data(addr, start_reg, length)

