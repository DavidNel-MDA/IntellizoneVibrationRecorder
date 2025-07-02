from DeviceSettings.accel_settings import ACCELEROMETER_CONFIG

class Accelerometer:
    def __init__(self, device):
        self.device = device
        self.scale_mg_per_lsb = ACCELEROMETER_CONFIG["Sensitivity_mg_per_lsb"]

    def configure(self):
        register = ACCELEROMETER_CONFIG["Accelerometer_Control_6"]
        value = ACCELEROMETER_CONFIG["Accelerometer_Control_6_Value"]
        self.device.write_byte("AG", register, value)

    def read_acceleration(self):
        register = ACCELEROMETER_CONFIG["Accelerometer_X_Low"]
        raw = self.device.read_bytes("AG", register, 6)

        def to_signed(lo, hi):
            return int.from_bytes([lo, hi], byteorder="little", signed=True)

        return {
            "x": to_signed(raw[0], raw[1]) * self.scale_mg_per_lsb,
            "y": to_signed(raw[2], raw[3]) * self.scale_mg_per_lsb,
            "z": to_signed(raw[4], raw[5]) * self.scale_mg_per_lsb,
        }

    def read_acceleration_g(self):
        mg_data = self.read_acceleration()
        return {axis: mg / 1000.0 for axis, mg in mg_data.items()}
