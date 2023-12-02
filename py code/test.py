import sys
import pyvisa as visa  # PyVISA library
import numpy as np
import struct
import time


ADDRESS = 'USB0::0x0957::0x17BC::MY52400362::0::INSTR'

rm = visa.ResourceManager()

osc = rm.open_resource(ADDRESS)

osc.timeout = 10000


osc.write(':CHANnel1:DISPlay ON')
osc.write(':EXT:DISPlay OFF')

osc.write(":TRIGger:MODE EDGE")
osc.write('TRIGger:EDGE:SOURce CHANnel1')
osc.write('TRIGger:EDGE:LEVel 10')
osc.write(":TRIGger:EDGE:SLOPe POSitive")
osc.query('*OPC?')
osc.write(":CHANnel1:SCALe 10")
osc.query('*OPC?')
osc.write(":CHANnel1:OFFSet 0")
osc.write(":TIMebase:SCALe 5E-4")
osc.write(":TIMebase:POSition 0.0")
osc.query('*OPC?')
# Set the acquisition type.
osc.write(":ACQuire:TYPE NORMal")
osc.query('*OPC?')

# Get numeric values for later calculations.
x_increment = osc.query(":WAVeform:XINCrement?")
x_origin = osc.query(":WAVeform:XORigin?")
y_increment = osc.query(":WAVeform:YINCrement?")
y_origin = osc.query(":WAVeform:YORigin?")
y_reference = osc.query(":WAVeform:YREFerence?")


# =========================================================
# Send a query, check for errors, return string:
# =========================================================
def do_query_ieee_block(query):
    osc.WriteString("%s" % query, True)
    result = osc.ReadIEEEBlock(VisaComLib.BinaryType_UI1, \
        False, True)
    check_instrument_errors(query)
    return result

# =========================================================
# Check for instrument errors:
# =========================================================
def check_instrument_errors(command):
    while True:
        osc.WriteString(":SYSTem:ERRor?", True)
        error_string = osc.ReadString()
        if error_string: # If there is an error string value.
            if error_string.find("+0,", 0, 3) == -1: # Not "No error".
                print("ERROR: %s, command: '%s'" % (error_string, command))
                print("Exited because of error.")
                sys.exit(1)
            
        else: # "No error"
            break
        
    else: # :SYSTem:ERRor? should always return string.
        print("ERROR: :SYSTem:ERRor? returned nothing, command: '%s'" \
         % command)
        print("Exited because of error.")
        sys.exit(1)

""" # Get the waveform data.
data_bytes = do_query_ieee_block(":WAVeform:DATA?")
nLength = len(data_bytes)
print("Number of data values: %d" % nLength)
# Open file for output.
strPath = "waveform_data.csv"
f = open(strPath, "w")
# Output waveform data in CSV format.
for i in range(0, nLength - 1):
    time_val = x_origin + (i * x_increment)
    voltage = (data_bytes[i] - y_reference) * y_increment + y_origin
    f.write("%E, %f\n" % (time_val, voltage))
# Close output file.
f.close()
print("Waveform format BYTE data written to %s." % strPath) """


# Get the waveform data.
#sData = osc.query_binary_values(c)
osc.write('WAVeform:FORMat WORD')
#sData = osc.query_binary_values(':WAVeform:DATA?', datatype = 's',is_big_endian = False)
sData = osc.query_binary_values(':WAVeform:DATA?')
#values = struct.unpack("%dB" % len(sData[2]), sData)
for i in range(len(sData)):
    print(struct.unpack('!f',struct.pack('!I',sData[i]))[0])
    #print(float(i))

print(x_increment,x_origin,y_increment,y_origin,y_reference)
#print(values[5],float(values[6]))
#print("Number of data values: %d" % len(values))
# =============================================================================
# Create unique file name with date/time tag
# =============================================================================



DIRECTORY = 'C:\\Users\\Public\\'

time_stamp = time.localtime()
year = time_stamp[0]
month = time_stamp[1]
day = time_stamp[2]
hour = time_stamp[3]
minute = time_stamp[4]
second = time_stamp[5]
date_stamp = '{:d}'.format(year) + '-' + '{:0>2d}'.format(month) + '-' + \
            '{:0>2d}'.format(day) + '_' + '{:0>2d}'.format(hour) + '-' + \
            '{:0>2d}'.format(minute) + '-' + '{:0>2d}'.format(second)

filename = DIRECTORY + date_stamp

# Save waveform data values to CSV file.
f = open(filename + '.csv', "w")
for i in range(0, len(sData) - 1):
    time_val = x_origin + (i * x_increment)
    voltage = (sData[i] - y_reference) * y_increment + y_origin
    print(voltage)
    f.write("%E, %f\n" % (time_val, voltage))
f.close()

osc.close