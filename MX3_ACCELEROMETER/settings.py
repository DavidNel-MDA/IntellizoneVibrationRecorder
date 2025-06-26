from config_yaml import ACCELEROMETER_SETTINGS

# Labels (selected per deployment mode, CLI, or runtime condition)
ODR_LABEL = "952_Hz"
FS_LABEL = "±2g"
BW_SCAL_ODR_LABEL = "Auto"
BW_XL_LABEL = "408Hz"

CTRL6_LOOKUP = ACCELEROMETER_SETTINGS["Accelerometer_Control_6"]

ODR = CTRL6_LOOKUP["Output_Data_Rate"][ODR_LABEL]
FS = CTRL6_LOOKUP["Full_Scale_Selection"][FS_LABEL]
BW_SCAL_ODR = CTRL6_LOOKUP["Bandwidth_Scaling"][BW_SCAL_ODR_LABEL]
BW_XL = CTRL6_LOOKUP["Bandwidth_Filter"][BW_XL_LABEL]

CTRL6_VALUE = ((ODR & 0b111) << 5) | ((FS & 0b11) << 3) | ((BW_SCAL_ODR & 0b1) << 2) | (BW_XL & 0b11)
