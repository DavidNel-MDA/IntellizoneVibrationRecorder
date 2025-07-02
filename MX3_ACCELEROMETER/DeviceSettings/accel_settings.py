from config_yaml import LSM9DS1_CONFIG

# Extract relevant sections from YAML config
REG = LSM9DS1_CONFIG["ACCELEROMETER_GYROSCOPE_REGISTER"]
ACC6 = REG["READ_WRITE"]["CONTROL_REGISTER"]["Accelerometer_Control_6"]

# Extract bitfield values from YAML
ACC_ODR = ACC6["Output_Data_Rate"]["952Hz"]
ACC_FS_BITVAL = ACC6["Full_Scale_Selection"]["±2g"]
ACC_BW_SCALE = 1 if ACC6["Bandwidth_Scaling"]["Auto"] else 0
ACC_BW = ACC6["Bandwidth_Filter"]["408Hz"]

# Bit-pack the control register value
ACC_CTRL6_VAL = (
    (ACC_ODR & 0b111) << 5 |
    (ACC_FS_BITVAL & 0b11) << 3 |
    (ACC_BW_SCALE & 0b1) << 2 |
    (ACC_BW & 0b11)
)

# Invert Full_Scale_Selection to lookup string key from bit value
fs_mapping = ACC6["Full_Scale_Selection"]
fs_value_to_key = {v: k for k, v in fs_mapping.items()}
fs_key = fs_value_to_key[ACC_FS_BITVAL]

# Sensitivity table in mg/LSB based on FS string
scale_map = {
    "±2g": 0.061,
    "±4g": 0.122,
    "±8g": 0.244,
    "±16g": 0.732,
}
sensitivity = scale_map[fs_key]

# Export final settings dictionary
ACCELEROMETER_CONFIG = {
    "Accelerometer_Control_6": REG["Accelerometer_Control_6"],
    "Accelerometer_Control_6_Value": ACC_CTRL6_VAL,
    "Accelerometer_X_Low": REG["Accelerometer_X_Low"],
    "Sensitivity_mg_per_lsb": sensitivity
}