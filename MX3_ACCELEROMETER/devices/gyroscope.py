from settings import GYROSCOPE_CONFIG

class Gyroscope:
    def __init__(self, device):
        self.device = device

    def configure(self):
        register = GYROSCOPE_CONFIG["Gyroscope_Control_1"]
        value = GYROSCOPE_CONFIG["Gyroscope_Control_1_Value"]
        self.device.write_byte("AG", register, value)

    def read_angular_velocity(self):
        register = GYROSCOPE_CONFIG["Gyroscope_X_Low"]
        raw = self.device.read_bytes("AG", register, 6)
        def to_signed(lo, hi): return int.from_bytes([lo, hi], "little", signed=True)
        return {
            "x": to_signed(raw[0], raw[1]),
            "y": to_signed(raw[2], raw[3]),
            "z": to_signed(raw[4], raw[5]),
        }
