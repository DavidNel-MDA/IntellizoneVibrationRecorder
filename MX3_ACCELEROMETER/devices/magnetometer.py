from settings import LSM9DS1_MAG_CONFIG

class Magnetometer:
    def __init__(self, device):
        self.device = device

    def configure(self):
        self.device.write_byte("MAG", LSM9DS1_MAG_CONFIG["Magnetic_Control_1"], LSM9DS1_MAG_CONFIG["Magnetic_Control_1_Value"])
        self.device.write_byte("MAG", LSM9DS1_MAG_CONFIG["Magnetic_Control_2"], LSM9DS1_MAG_CONFIG["Magnetic_Control_2_Value"])
        self.device.write_byte("MAG", LSM9DS1_MAG_CONFIG["Magnetic_Control_3"], LSM9DS1_MAG_CONFIG["Magnetic_Control_3_Value"])

    def read_magnetic_field(self):
        register = LSM9DS1_MAG_CONFIG["Magnetic_X_Low"]
        raw = self.device.read_bytes("MAG", register, 6)
        def to_signed(lo, hi): return int.from_bytes([lo, hi], "little", signed=True)
        return {
            "x": to_signed(raw[0], raw[1]),
            "y": to_signed(raw[2], raw[3]),
            "z": to_signed(raw[4], raw[5]),
        }
