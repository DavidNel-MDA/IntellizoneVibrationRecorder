from config_yaml import LSM9DS1_CONFIG

REG = LSM9DS1_CONFIG["ACCELEROMETER_GYROSCOPE_REGISTER"]
GYRO = REG["READ_WRITE"]["CONTROL_REGISTER"]["Gyroscope_Control_1"]

fs_bit_value = GYRO["Full_Scale_Selection"]["245dps"]  # or dynamic if needed

# Invert mapping to get "245dps", etc.
fs_key = {v: k for k, v in GYRO["Full_Scale_Selection"].items()}[fs_bit_value]

scale_map = {
    "245dps": 8.75,  # mdps/LSB
    "500dps": 17.5,
    "2000dps": 70.0,
}

GYROSCOPE_CONFIG = {
    "Gyroscope_Control_1": REG["Gyroscope_Control_1"],
    "Gyroscope_Control_1_Value": (
        (GYRO["Output_Data_Rate"]["952Hz"] << 5)
        | (fs_bit_value << 3)
        | (GYRO["Bandwidth_Selection"]["BW1"])
    ),
    "Gyroscope_X_Low": REG["Gyroscope_X_Low"],
    "Sensitivity_mdps_per_lsb": scale_map[fs_key],
}
