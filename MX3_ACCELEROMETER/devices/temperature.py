from DeviceSettings.temp_settings import TEMPERATURE_CONFIG

class TemperatureSensor:
    def __init__(self, device):
        self.device = device

    def read_temperature_raw(self):
        reg = TEMPERATURE_CONFIG["Temperature_Output_Low"]
        raw = self.device.read_bytes("AG", reg, 2)
        return int.from_bytes(raw, byteorder="little", signed=True)

    def read_temperature_celsius(self):
        raw_temp = self.read_temperature_raw()
        # From LSM9DS1 datasheet: Temp in deg C = 25 + (raw / 16)
        return 25.0 + (raw_temp / 16.0)
