import pyvisa
import struct
import sys

addr = "USB0::0x2A8D::0x039B::CN60531137::0::INSTR" #EDUX1052G

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

def do_query_string(query):
    #if debug:
    #    print(f"Qys = '{query}'")
    result = InfiniiVision.query(f"{query}")
    check_instrument_errors(query)
    return result.strip()
        

rm = pyvisa.ResourceManager("C:\\Windows\\System32\\visa64.dll")
InfiniiVision = rm.open_resource(addr)
InfiniiVision.timeout = 15000
InfiniiVision.clear()
InfiniiVision.write(":CHANnel1:SCALe 0.05")
qresult = do_query_string(f":CHANnel1:SCALe?")
print(f"CHANnel1 vertical scale: {qresult}")
    
InfiniiVision.write(":TRIGger:EDGE:SOURce CHANnel2")
qresult = do_query_string(":TRIGger:EDGE:SOURce?")
print(f"Trigger edge source: {qresult}")