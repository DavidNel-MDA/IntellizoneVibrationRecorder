from DeviceSettings.gyro_settings import GYROSCOPE_CONFIG

class Gyroscope:
    def __init__(self, device):
        self.device = device
        self.scale_mdps_per_lsb = GYROSCOPE_CONFIG["Sensitivity_mdps_per_lsb"]

    def configure(self):
        reg = GYROSCOPE_CONFIG["Gyroscope_Control_1"]
        value = GYROSCOPE_CONFIG["Gyroscope_Control_1_Value"]
        self.device.write_byte("AG", reg, value)

    def read_angular_velocity(self):
        reg = GYROSCOPE_CONFIG["Gyroscope_X_Low"]
        raw = self.device.read_bytes("AG", reg, 6)

        def to_signed(lo, hi):
            return int.from_bytes([lo, hi], byteorder="little", signed=True)

        return {
            "x": to_signed(raw[0], raw[1]) * self.scale_mdps_per_lsb,
            "y": to_signed(raw[2], raw[3]) * self.scale_mdps_per_lsb,
            "z": to_signed(raw[4], raw[5]) * self.scale_mdps_per_lsb,
        }

    def read_angular_velocity_dps(self):
        mdps = self.read_angular_velocity()
        return {axis: val / 1000.0 for axis, val in mdps.items()}
