from config_yaml import LSM9DS1_CONFIG

REG = LSM9DS1_CONFIG["MAGNETOMETER_REGISTER"]
CTRL = REG["READ_WRITE"]["CONTROL_REGISTER"]

# Magnetic Control 1
CTRL1 = CTRL["Magnetic_Control_1"]
odr = CTRL1["Output_Data_Rate"]["80Hz"]
temp_comp = CTRL1["Temperature_Compensation"]["Enabled"]
xy_mode = CTRL1["X_Y_Operative_Mode"]["High_Performance_Mode"]
ctrl1_val = ((temp_comp & 0x1) << 7) | ((xy_mode & 0x3) << 5) | ((odr & 0x7) << 2)

# Magnetic Control 2
CTRL2 = CTRL["Magnetic_Control_2"]
fs = CTRL2["Full_Scale_Configuration"]["4_Gauss"]
ctrl2_val = (fs & 0x3) << 5

# Magnetic Control 3
CTRL3 = CTRL["Magnetic_Control_3"]
mode = CTRL3["Operating_Mode"]["Continuous_Conversion"]
ctrl3_val = (mode & 0x3)

# Sensitivity (from FS string)
fs_key = {v: k for k, v in CTRL2["Full_Scale_Configuration"].items()}[fs]
scale_map = {
    "4_Gauss": 0.14,
    "8_Gauss": 0.29,
    "12_Gauss": 0.43,
    "16_Gauss": 0.58,
}
sensitivity = scale_map[fs_key]

# Export configuration
LSM9DS1_MAG_CONFIG = {
    "Magnetic_Control_1": REG["Magnetic_Control_1"],
    "Magnetic_Control_1_Value": ctrl1_val,
    "Magnetic_Control_2": REG["Magnetic_Control_2"],
    "Magnetic_Control_2_Value": ctrl2_val,
    "Magnetic_Control_3": REG["Magnetic_Control_3"],
    "Magnetic_Control_3_Value": ctrl3_val,
    "Magnetic_X_Low": REG["Magnetic_X_Low"],
    "Sensitivity_mgauss_per_lsb": sensitivity,
}
