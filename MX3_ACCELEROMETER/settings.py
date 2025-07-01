from config_yaml import LSM9DS1_CONFIG

# Shortcuts to nested blocks
REG = LSM9DS1_CONFIG.get("ACCELEROMETER_GYROSCOPE_REGISTER", {})
MAG_REG = LSM9DS1_CONFIG.get("MAGNETOMETER_REGISTER", {})
ACC6 = LSM9DS1_CONFIG.get("Accelerometer_Control_6", {})
MAG_CTL = LSM9DS1_CONFIG.get("Magnetometer_Control", {})
GYRO_CTL = REG.get("READ_WRITE", {}).get("CONTROL_REGISTER", {}).get("Gyroscope_Control_1", {})

# ----------------------------------------
# ACCELEROMETER CONFIGURATION
# ----------------------------------------

ACC_ODR = ACC6.get("Output_Data_Rate", {}).get("952_Hz", 0b110)
ACC_FS = ACC6.get("Full_Scale_Selection", {}).get("±2g", 0b00)
ACC_BW_SCALE = 1 if ACC6.get("Bandwidth_Scaling", {}).get("Auto", False) else 0
ACC_BW = ACC6.get("Bandwidth_Filter", {}).get("408Hz", 0b00)

ACC_CTRL6_VAL = (
    (ACC_ODR & 0b111) << 5 |
    (ACC_FS & 0b11) << 3 |
    (ACC_BW_SCALE & 0b1) << 2 |
    (ACC_BW & 0b11)
)

ACCELEROMETER_CONFIG = {
    "Accelerometer_Control_6_Value": ACC_CTRL6_VAL,
    "Accelerometer_Control_6": REG.get("Accelerometer_Control_6", 0x20),
    "Accelerometer_X_Low": REG.get("Accelerometer_X_Low", 0x28)
}

# ----------------------------------------
# MAGNETOMETER CONFIGURATION
# ----------------------------------------

MAG_ODR = MAG_CTL.get("Output_Data_Rate", {}).get("80Hz", 0b111)
MAG_FS = MAG_CTL.get("Full_Scale_Selection", {}).get("±4gauss", 0b00)
MAG_XY_MODE = MAG_CTL.get("XY_Operating_Mode", {}).get("HighPerformance", 0b10)
MAG_Z_MODE = MAG_CTL.get("Z_Operating_Mode", {}).get("HighPerformance", 0b10)
MAG_MODE_SELECT = MAG_CTL.get("Mode", {}).get("Continuous", 0b00)

MAG_CTRL1_VAL = (1 << 7) | (MAG_XY_MODE << 5) | (MAG_ODR << 2)
MAG_CTRL2_VAL = MAG_FS << 5
MAG_CTRL3_VAL = MAG_MODE_SELECT

LSM9DS1_MAG_CONFIG = {
    "Magnetic_Control_1_Value": MAG_CTRL1_VAL,
    "Magnetic_Control_2_Value": MAG_CTRL2_VAL,
    "Magnetic_Control_3_Value": MAG_CTRL3_VAL,
    "Magnetic_Control_1": MAG_REG.get("Magnetic_Control_1", 0x20),
    "Magnetic_Control_2": MAG_REG.get("Magnetic_Control_2", 0x21),
    "Magnetic_Control_3": MAG_REG.get("Magnetic_Control_3", 0x22),
    "Magnetic_X_Low": MAG_REG.get("Magnetic_X_Low", 0x28)
}

# ----------------------------------------
# GYROSCOPE CONFIGURATION
# ----------------------------------------

GYRO_ODR = GYRO_CTL.get("Output_Data_Rate", {}).get("952Hz", 0b111)
GYRO_FS = GYRO_CTL.get("Full_Scale_Selection", {}).get("245dps", 0b00)
GYRO_BW = GYRO_CTL.get("Bandwidth_Selection", {}).get("BW1", 0b00)

GYRO_CTRL1_VAL = (
    (GYRO_ODR & 0b111) << 5 |
    (GYRO_FS & 0b11) << 3 |
    (GYRO_BW & 0b11)
)

GYROSCOPE_CONFIG = {
    "Gyroscope_Control_1_Value": GYRO_CTRL1_VAL,
    "Gyroscope_Control_1": REG.get("Gyroscope_Control_1", 0x10),
    "Gyroscope_X_Low": REG.get("Gyroscope_X_Low", 0x18)
}

# ----------------------------------------
# TEMPERATURE CONFIGURATION
# ----------------------------------------

TEMPERATURE_CONFIG = {
    "Temperature_Output_Low": REG.get("Temperature_Output_Low", 0x15),
    "Temperature_Output_High": REG.get("Temperature_Output_High", 0x16),
    "Temperature_Base_Register": REG.get("Temperature_Output_Low", 0x15)
}
