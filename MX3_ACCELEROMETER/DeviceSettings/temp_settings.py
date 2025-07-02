from config_yaml import LSM9DS1_CONFIG

# Shortcuts to nested blocks
REG = LSM9DS1_CONFIG.get("ACCELEROMETER_GYROSCOPE_REGISTER", {})

TEMPERATURE_CONFIG = {
    "Temperature_Output_Low": REG.get("Temperature_Output_Low", 0x15),
    "Temperature_Output_High": REG.get("Temperature_Output_High", 0x16),
    "Temperature_Base_Register": REG.get("Temperature_Output_Low", 0x15),
}
