# file for calibration files reader
import configparser


# Get Array with all Values
def get_calibration_values(serial_number):
    # Set up Configparser
    calibration_file = configparser.ConfigParser()
    calibration_file.read('IRC081 Calibration.ini')
    # Create output array , write values and return
    output_array = []
    for key in calibration_file[serial_number]:
        key_value = calibration_file[serial_number][key]
        output_array.append(key_value)
    return output_array
