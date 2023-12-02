# -*- coding: utf-8 -*-
# *********************************************************
# This program illustrates a few commonly-used programming
# features of your Keysight oscilloscope.
# *********************************************************
# Import modules.
# ---------------------------------------------------------
import pyvisa
import struct
import sys
import time
import signal
import numpy as np

addr = "USB0::0x0957::0x17BC::MY52400362::0::INSTR" #EDUX1052G
#addr = "USB0::0x0957::0x17BC::MY52400362::0::INSTR" #MSO-X 4154A
#addr = "USB0::0x0957::0x17A4::MY51138829::0::INSTR" #DSO334A

#addr =

# Global variables.
# ---------------------------------------------------------
input_channel = "CHANnel"
# input_channel = "CHANnel2"
setup_file_name = "setup.scp"
screen_image_file_name = "screen_image.png"
waveform_data_file_name = "waveform_data.csv"
#wfm_fmt = "BYTE"
wfm_fmt = "WORD"
TriggerSrc = "CHANnel1"
# TriggerSrc = "CHANnel2"
TIMebaseSCALe = '7e-3' #EDUX1052G min: 5E-9; 4154A min: 5E-10
CHANnel1SCALe = '0.05' # 4154A 1mV - 5V; 
# CHANnel1SCALe = '0.5' # 4154A 1mV - 5V; 
OFFSet = '0.12'
WAVeformPOINts = '5E4' # raw mode maximum # of point = timeScal * 1E10 // 5e-4 timeScale & 5e4 pts for MSO
# 4154A 1MHz input 5e-6 timebase 500 numpoints GOOD

# =========================================================
# Logging termination:
# =========================================================
def handler(signum, frame):
    global endNow
    print("Ctrl-c was pressed. Ending log.")
    endNow = True

# =========================================================
# Initialize:
# =========================================================
def initialize():
    
    # Get and display the device's *IDN? string.
    idn_string = do_query_string("*IDN?")
    print(f"Identification string: '{idn_string}'")
    
    # Clear status and load the default setup.
    InfiniiVision.write("*CLS")
    InfiniiVision.write("*RST")
    
# =========================================================
# Capture:
# =========================================================
def capture():
    # Use auto-scale to automatically set up oscilloscope.
    #print("Autoscale.")
    #InfiniiVision.write(":AUToscale")
    
    # Set trigger mode.
    InfiniiVision.write(":TRIGger:MODE EDGE")
    qresult = do_query_string(":TRIGger:MODE?")
    print(f"Trigger mode: {qresult}")
    
    # Set EDGE trigger parameters.
    InfiniiVision.write(f":TRIGger:EDGE:SOURce {TriggerSrc}")
    qresult = do_query_string(":TRIGger:EDGE:SOURce?")
    print(f"Trigger edge source: {qresult}")

    InfiniiVision.write(":TRIGger:EDGE:LEVel 0.1")
    qresult = do_query_string(":TRIGger:EDGE:LEVel?")
    print(f"Trigger edge level: {qresult}")
    
    InfiniiVision.write(":TRIGger:EDGE:SLOPe POSitive")
    qresult = do_query_string(":TRIGger:EDGE:SLOPe?")
    print(f"Trigger edge slope: {qresult}")
    
    # Save oscilloscope setup.
    setup_bytes = do_query_ieee_block(":SYSTem:SETup?")
    
    f = open(setup_file_name, "wb")
    f.write(setup_bytes)
    f.close()
    print(f"Setup bytes saved: {len(setup_bytes)}")
    
    # Change oscilloscope settings with individual commands:
    
    # Set vertical scale and offset.
    InfiniiVision.write(f":{input_channel}:SCALe {CHANnel1SCALe}")
    qresult = do_query_string(f":{input_channel}:SCALe?")
    print(f"{input_channel} vertical scale: {qresult}")
    
    InfiniiVision.write(f":{input_channel}:OFFSet {OFFSet}")
    qresult = do_query_string(f":{input_channel}:OFFSet?")
    print(f"{input_channel} offset: {qresult}")
    
    # Set horizontal scale and offset.
    InfiniiVision.write(f":TIMebase:SCALe {TIMebaseSCALe}")
    qresult = do_query_string(":TIMebase:SCALe?")
    print(f"Timebase scale: {qresult}")
    
    InfiniiVision.write(":TIMebase:POSition 0.0")
    qresult = do_query_string(":TIMebase:POSition?")
    print(f"Timebase position: {qresult}")
    
    # Set the acquisition type.
    InfiniiVision.write(":ACQuire:TYPE NORMal")
    qresult = do_query_string(":ACQuire:TYPE?")
    print(f"Acquire type: {qresult}\n\n")
    
    # Or, set up oscilloscope by loading a previously saved setup.
    #setup_bytes = ""
    #f = open(setup_file_name, "rb")
    #setup_bytes = f.read()
    #f.close()
    #do_command_ieee_block(":SYSTem:SETup", setup_bytes)
    #print(f"Setup bytes restored: {len(setup_bytes)}")
    
    # Capture an acquisition using :DIGitize.
    InfiniiVision.write(f":DIGitize {input_channel}")
    
    # Make measurements.
    # --------------------------------------------------------
    InfiniiVision.write(f":MEASure:SOURce {input_channel}")
    qresult = do_query_string(":MEASure:SOURce?")
    print(f"Measure source: {qresult}")
    InfiniiVision.write(":MEASure:FREQuency")
    qresult = do_query_string(":MEASure:FREQuency?")
    print(f"Measured frequency on {input_channel}: {qresult}")
    InfiniiVision.write(":MEASure:VAMPlitude")
    qresult = do_query_string(":MEASure:VAMPlitude?")
    print(f"Measured vertical amplitude on {input_channel}: {qresult}")
    # Download the screen image.
    # --------------------------------------------------------
    InfiniiVision.write(":HARDcopy:INKSaver OFF")
    screen_bytes = do_query_ieee_block(":DISPlay:DATA? PNG, COLor")
    
    # Save display data values to file.
    f = open(screen_image_file_name, "wb")
    f.write(screen_bytes)
    f.close()
    print(f"Screen image written to {screen_image_file_name}.")
    # Download waveform data.
    # --------------------------------------------------------
    
    # Set the waveform source.
    InfiniiVision.write(f":WAVeform:SOURce {input_channel}")
    qresult = do_query_string(":WAVeform:SOURce?")
    print(f"Waveform source: {qresult}")
    
# =========================================================
# Analyze:
# =========================================================
def analyze():
    
    # Set the waveform points mode.
    InfiniiVision.write(":WAVeform:POINts:MODE RAW")
    qresult = do_query_string(":WAVeform:POINts:MODE?")
    print(f"Waveform points mode: {qresult}")

    # Get the number of waveform points available.
    InfiniiVision.write(f":WAVeform:POINts {WAVeformPOINts}")
    qresult = do_query_string(":WAVeform:POINts?")
    print(f"Waveform points available: {qresult}")
    
    # Choose the format of the data returned (BYTE or WORD):
    InfiniiVision.write(f":WAVeform:FORMat {wfm_fmt}")
    qresult = do_query_string(":WAVeform:FORMat?")
    print(f"Waveform format: {qresult}")

    # Specify the byte order in WORD data.
    if wfm_fmt == "WORD":
        InfiniiVision.write(":WAVeform:BYTeorder LSBF")
        qresult = do_query_string(":WAVeform:BYTeorder?")
        print(f"Waveform byte order for WORD data: {qresult}")

    # Display the waveform settings from preamble:
    wav_form_dict = {
     0 : "BYTE",
     1 : "WORD",
     4 : "ASCii",
    }
    acq_type_dict = {
     0 : "NORMal",
     1 : "PEAK",
     2 : "AVERage",
     3 : "HRESolution",
    }
    
    preamble_string = do_query_string(":WAVeform:PREamble?")
    (
     wav_form, acq_type, wfmpts, avgcnt, x_increment, x_origin,
     x_reference, y_increment, y_origin, y_reference
    ) = preamble_string.split(",")
    
    print(f"Waveform format: {wav_form_dict[int(wav_form)]}")
    print(f"Acquire type: {acq_type_dict[int(acq_type)]}")
    print(f"Waveform points desired: {wfmpts}")
    print(f"Waveform average count: {avgcnt}")
    print(f"Waveform X increment: {x_increment}")
    print(f"Waveform X origin: {x_origin}")
    print(f"Waveform X reference: {x_reference}") # Always 0.
    print(f"Waveform Y increment: {y_increment}")
    print(f"Waveform Y origin: {y_origin}")
    print(f"Waveform Y reference: {y_reference}")
    
    # Get numeric values for later calculations.
    x_increment = do_query_number(":WAVeform:XINCrement?")
    x_origin = do_query_number(":WAVeform:XORigin?")
    y_increment = do_query_number(":WAVeform:YINCrement?")
    y_origin = do_query_number(":WAVeform:YORigin?")
    y_reference = do_query_number(":WAVeform:YREFerence?")
    
    # Get the waveform data.
  
    
    logging_arrayAppending(50, x_increment, x_origin, y_increment, y_origin, y_reference)
    #logging_csvSegement(10)
    #logging_full(5, x_increment, x_origin, y_increment, y_origin, y_reference)
    
    print(f"Waveform format {wfm_fmt} data written to {date_stamp}.csv.")

# =========================================================
# Logging_arrayAppending:
# =========================================================
def logging_arrayAppending(iteration, x_increment, x_origin, y_increment, y_origin, y_reference):
    
    t0 = time.perf_counter()
    a = np.array([])
    t = np.array([])
    t0 = time.perf_counter()
    
    print('Logging data...')
    """ signal.signal(signal.SIGINT, handler)
    endNow = False
    while not endNow: """
    for i in range (0, iteration):
        
        t = np.append(t, time.perf_counter())
        data_bytes = np.array(do_query_ieee_block(":WAVeform:DATA?"))
        a = np.append(a, data_bytes)
    
    time.sleep(2)
    print("Saving data to CSV")   
    print(f"length of array {len(a)}")
    
    # Save to csv
    filename = f"{date_stamp}.csv"
    f = open(filename, "w")
    
    for i in range (0, len(a)):
        
        print(f'Writing cycle {i}')
        start_time = t[i] - t0
        temp_a = a[i]
        data_bytes_length = len(temp_a)
        
        values = unpackBinary(wfm_fmt, data_bytes_length,temp_a)
        
        #print(f"Number of data values: {len(values)}")
        #print(start_time)
        
        for i in range(0, len(values)-1):
            time_val = start_time + x_origin + (i * x_increment)
            voltage = ((values[i] - y_reference) * y_increment) + y_origin
            f.write(f"{time_val:E}, {voltage:f}\n")

    # Close output file.
    f.close
        #print(f"Number of data values: {len(values)}") """

# =========================================================
# Logging_csvSegement
# =========================================================
def logging_csvSegement(iteration):
    filename = f"{date_stamp}.csv"
    f = open(filename, "w")
    
    t0 = time.perf_counter()
    for i in range (1, iteration):
        data_bytes = do_query_ieee_block(":WAVeform:DATA?")
        data_bytes_length = len(data_bytes)
        #print(data_bytes_length)
        
        for i in range(0, data_bytes_length):
            f.write(f'{data_bytes[i]}\n')
            #print iteration and time stamp
        print(f"time interval {i}: {time.perf_counter() - t0}")
        
    # Close output file.
    f.close()

# =========================================================
# logging_full
# =========================================================
def logging_full(iteration, x_increment, x_origin, y_increment, y_origin, y_reference):
    filename = f"{date_stamp}.csv"
    f = open(filename, "w")
    
    t0 = time.perf_counter()
 
    for i in range (1, iteration):
        data_bytes = do_query_ieee_block(":WAVeform:DATA?")
    
        #print iteration and time stamp
        print(f"time interval {i}: {time.perf_counter() - t0}")
    
        #print(data_bytes_length)
        data_bytes_length = len(data_bytes)
        print(f"Byte count: {data_bytes_length}")
        
        values = unpackBinary(wfm_fmt, data_bytes_length,data_bytes)
        
        #print(f"Number of data values: {len(values)}")
        
        for i in range(0, len(values) - 1):
            time_val = (time.perf_counter()-t0) + x_origin + (i * x_increment)
            voltage = ((values[i] - y_reference) * y_increment) + y_origin
            f.write(f"{time_val:E}, {voltage:f}\n")
    
    # Close output file.
    f.close()

# =========================================================
# Unpack binary values
# =========================================================
def unpackBinary(wfm_fmt, data_bytes_length,temp_a):
    if wfm_fmt == "BYTE":
        block_points = data_bytes_length
    elif wfm_fmt == "WORD":
        block_points = data_bytes_length / 2
        
    #Unpack or split into list of data values.
    if wfm_fmt == "BYTE":
        values = struct.unpack("%dB" % block_points, temp_a)
    elif wfm_fmt == "WORD":
        values = struct.unpack("%dH" % block_points, temp_a)
    return(values)

# =========================================================
# Send a command and check for errors:
# =========================================================
def do_command(command, hide_params=False):
    
    if hide_params:
        (header, data) = command.split(" ", 1)
        #if debug:
        #    print(f"Cmd = '{header}'")
        #else:
        #    if debug:
        #        print(f"Cmd = '{command}'")
        InfiniiVision.write(f"{command}")
    
    if hide_params:
        check_instrument_errors(header)
    else:
        check_instrument_errors(command)

# =========================================================
# Send a command and binary values and check for errors:
# =========================================================
def do_command_ieee_block(command, values):
    #if debug: print(f"Cmb = '{command}'")
    InfiniiVision.write_binary_values(f"{command} ", values, datatype='B')
    check_instrument_errors(command)
    
# =========================================================
# Send a query, check for errors, return string:
# =========================================================
def do_query_string(query):
    #if debug:
    #    print(f"Qys = '{query}'")
    result = InfiniiVision.query(f"{query}")
    check_instrument_errors(query)
    return result.strip()

# =========================================================
# Send a query, check for errors, return floating-point value:
# =========================================================
def do_query_number(query):
    #if debug:
    #    print(f"Qyn = '{query}'")
    results = InfiniiVision.query(f"{query}")
    check_instrument_errors(query)
    return float(results)

# =========================================================
# Send a query, check for errors, return binary values:
# =========================================================
def do_query_ieee_block(query):
    #if debug:
    #    print(f"Qyb = '{query}'")
    result = InfiniiVision.query_binary_values(f"{query}", datatype='s', container=bytes)
    check_instrument_errors(query)
    return result
    
# =========================================================
# Check for instrument errors:
# =========================================================
def check_instrument_errors(command):
    while True:
        error_string = InfiniiVision.query(":SYSTem:ERRor?")
        if error_string: # If there is an error string value.
            if error_string.find("+0,", 0, 3) == -1: # Not "No error".
                print(f"ERROR: {error_string}, command: '{command}'")
                print("Exited because of error.")
                sys.exit(1)
            else: # "No error"
                break
        else: # :SYSTem:ERRor? should always return string.
            print(f"ERROR: :SYSTem:ERRor? returned nothing, command: '{command}'")
            print("Exited because of error.")
            sys.exit(1)

# =============================================================================
# Create unique file name with date/time tag
# =============================================================================

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

# =========================================================
# Main program:
# =========================================================
rm = pyvisa.ResourceManager("C:\\Windows\\System32\\visa64.dll")
InfiniiVision = rm.open_resource(addr)
InfiniiVision.timeout = 15000
InfiniiVision.clear()

# Initialize the oscilloscope, capture data, and analyze.



initialize()

#InfiniiVision.write(":WGEN:FREQuency 1E6")
#InfiniiVision.write(":WGEN:FUNCtion SINusoid")
#InfiniiVision.write(":WGEN:OUTPut 1")

capture()
analyze()

InfiniiVision.close()
print("End of program.")
sys.exit()