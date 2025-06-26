import smbus2
from bidict import bidict

class LSM9DS1Device:
    def __init__(self, bus_number: int, address: int, register_map: bidict):
        self.bus = smbus2.SMBus(bus_number)
        self.address = address
        self.register_map = register_map

    def write_register(self, register_name: str, value: int):
        reg = self.register_map[register_name]
        self.bus.write_byte_data(self.address, reg, value)

    def read_register(self, register_name: str) -> int:
        register = self.register_map[register_name]
        return self.bus.read_byte_data(self.address, register)

    def read_block(self, start_register: str, length: int) -> list[int]:
        register = self.register_map[start_register]
        return self.bus.read_i2c_block_data(self.address, register, length)

    def _combine_bytes(self, high: int, low: int) -> int:
        val = (high << 8) | low
        return val - 65536 if val > 32767 else val
