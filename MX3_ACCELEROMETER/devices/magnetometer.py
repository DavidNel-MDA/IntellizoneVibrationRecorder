from DeviceSettings.mag_settings import LSM9DS1_MAG_CONFIG


class Magnetometer:
    def __init__(self, device):
        self.device = device
        self.scale_mgauss_per_lsb = LSM9DS1_MAG_CONFIG["Sensitivity_mgauss_per_lsb"]

    def configure(self):
        cfg = LSM9DS1_MAG_CONFIG
        self.device.write_byte(
            "MAG", cfg["Magnetic_Control_1"], cfg["Magnetic_Control_1_Value"]
        )
        self.device.write_byte(
            "MAG", cfg["Magnetic_Control_2"], cfg["Magnetic_Control_2_Value"]
        )
        self.device.write_byte(
            "MAG", cfg["Magnetic_Control_3"], cfg["Magnetic_Control_3_Value"]
        )

    def read_magnetic_field(self):
        reg = LSM9DS1_MAG_CONFIG["Magnetic_X_Low"]
        raw = self.device.read_bytes("MAG", reg, 6)

        def to_signed(lo, hi):
            return int.from_bytes([lo, hi], byteorder="little", signed=True)

        return {
            "x": to_signed(raw[0], raw[1]) * self.scale_mgauss_per_lsb,
            "y": to_signed(raw[2], raw[3]) * self.scale_mgauss_per_lsb,
            "z": to_signed(raw[4], raw[5]) * self.scale_mgauss_per_lsb,
        }

    def read_magnetic_field_uT(self):
        """Return magnetic field in microtesla (µT)"""
        mgauss = self.read_magnetic_field()
        return {axis: val * 0.1 for axis, val in mgauss.items()}  # 1 mgauss = 0.1 µT
