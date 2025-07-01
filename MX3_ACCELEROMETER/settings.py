from config_yaml import LSM9DS1_CONFIG

# Extract nested dictionaries
ACCELEROMETER_CONTROL_6 = LSM9DS1_CONFIG.get("Accelerometer_Control_6", {})
ACCELEROMETER_GYROSCOPE_REGISTERS = LSM9DS1_CONFIG.get("ACCELEROMETER_GYROSCOPE_REGISTER", {})
MAGNETOMETER_REGISTERS = LSM9DS1_CONFIG.get("MAGNETOMETER_REGISTER", {})
MAGNETOMETER_CONTROL = LSM9DS1_CONFIG.get("Magnetometer_Control", {})

# ----------------------------------------
# ACCELEROMETER CONFIGURATION
# ----------------------------------------

Output_Data_Rate = ACCELEROMETER_CONTROL_6.get("Output_Data_Rate", {}).get("952_Hz", 0b110)
Full_Scale_Selection = ACCELEROMETER_CONTROL_6.get("Full_Scale_Selection", {}).get("±2g", 0b00)
Bandwidth_Scaling = 1 if ACCELEROMETER_CONTROL_6.get("Bandwidth_Scaling", {}).get("Auto", False) else 0
Bandwidth_Filter = ACCELEROMETER_CONTROL_6.get("Bandwidth_Filter", {}).get("408Hz", 0b00)

Accelerometer_Control_6_Value = (
    (Output_Data_Rate & 0b111) << 5 |
    (Full_Scale_Selection & 0b11) << 3 |
    (Bandwidth_Scaling & 0b1) << 2 |
    (Bandwidth_Filter & 0b11)
)

ACCELEROMETER_CONFIG = {
    "Accelerometer_Control_6_Value": Accelerometer_Control_6_Value,
    "Accelerometer_X_Low": ACCELEROMETER_GYROSCOPE_REGISTERS.get("Accelerometer_X_Low", 0x28),
    "Accelerometer_Control_6": ACCELEROMETER_GYROSCOPE_REGISTERS.get("Accelerometer_Control_6", 0x20)
}

# ----------------------------------------
# MAGNETOMETER CONFIGURATION
# ----------------------------------------

Magnetic_Output_Data_Rate = MAGNETOMETER_CONTROL.get("Output_Data_Rate", {}).get("80Hz", 0b111)
Magnetic_Full_Scale_Selection = MAGNETOMETER_CONTROL.get("Full_Scale_Selection", {}).get("±4gauss", 0b00)
XY_Operating_Mode = MAGNETOMETER_CONTROL.get("XY_Operating_Mode", {}).get("HighPerformance", 0b10)
Z_Operating_Mode = MAGNETOMETER_CONTROL.get("Z_Operating_Mode", {}).get("HighPerformance", 0b10)
Mode_Select = MAGNETOMETER_CONTROL.get("Mode", {}).get("Continuous", 0b00)

Magnetic_Control_1_Value = (1 << 7) | (XY_Operating_Mode << 5) | (Magnetic_Output_Data_Rate << 2)
Magnetic_Control_2_Value = (Magnetic_Full_Scale_Selection << 5)
Magnetic_Control_3_Value = Mode_Select

LSM9DS1_MAG_CONFIG = {
    "Magnetic_Control_1": MAGNETOMETER_REGISTERS.get("Magnetic_Control_1", 0x20),
    "Magnetic_Control_2": MAGNETOMETER_REGISTERS.get("Magnetic_Control_2", 0x21),
    "Magnetic_Control_3": MAGNETOMETER_REGISTERS.get("Magnetic_Control_3", 0x22),
    "Magnetic_X_Low": MAGNETOMETER_REGISTERS.get("Magnetic_X_Low", 0x28),
    "Magnetic_Control_1_Value": Magnetic_Control_1_Value,
    "Magnetic_Control_2_Value": Magnetic_Control_2_Value,
    "Magnetic_Control_3_Value": Magnetic_Control_3_Value
}

# ----------------------------------------
# GYROSCOPE CONFIGURATION
# ----------------------------------------

GYRO_CONTROL = ACCELEROMETER_GYROSCOPE_REGISTERS.get("READ_WRITE", {}).get("CONTROL_REGISTER", {}).get("Gyroscope_Control_1", {})

Gyroscope_Output_Data_Rate = GYRO_CONTROL.get("Output_Data_Rate", {}).get("952Hz", 0b111)
Gyroscope_Full_Scale_Selection = GYRO_CONTROL.get("Full_Scale_Selection", {}).get("245dps", 0b00)
Gyroscope_Bandwidth_Selection = GYRO_CONTROL.get("Bandwidth_Selection", {}).get("BW1", 0b00)

Gyroscope_Control_1_Value = (
    (Gyroscope_Output_Data_Rate & 0b111) << 5 |
    (Gyroscope_Full_Scale_Selection & 0b11) << 3 |
    (Gyroscope_Bandwidth_Selection & 0b11)
)

GYROSCOPE_CONFIG = {
    "Gyroscope_Control_1": ACCELEROMETER_GYROSCOPE_REGISTERS.get("Gyroscope_Control_1", 0x10),
    "Gyroscope_Control_1_Value": Gyroscope_Control_1_Value,
    "Gyroscope_X_Low": ACCELEROMETER_GYROSCOPE_REGISTERS.get("Gyroscope_X_Low", 0x18)
}

TEMPERATURE_CONFIG = {
    "Temperature_Output_Low": ACCELEROMETER_GYROSCOPE_REGISTERS.get("Temperature_Output_Low", 0x15),
    "Temperature_Output_High": ACCELEROMETER_GYROSCOPE_REGISTERS.get("Temperature_Output_High", 0x16)
}