import configparser
import ast

Serial_Number = '01FDA496'

#Get Array with all Values
def Get_calibration_values(serial_number):
	# Set up Configparser
	Calibration_File = configparser.ConfigParser()
	Calibration_File.read('IRC081 Calibration.ini')
	#Create output array , write values and return
	Output_Array = []
	for key in Calibration_File[Serial_Number]:
		key_value =  Calibration_File[serial_number][key]
		Output_Array.append(key_value)
	return(Output_Array)

print(Get_calibration_values(Serial_Number))