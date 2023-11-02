#!/bin/env python3

import pyvisa
import time
import signal
import numpy as np
import matplotlib.pyplot as plt

logfilename = "out.csv"
lcr_addr = "GPIB1::5::INSTR"


#Continuous mode
# DST
# DEND

rm = pyvisa.ResourceManager()

lcr = rm.open_resource(lcr_addr)

#lrns = lcr.query("*LRN?")
#print(lrns)
#lcr.clear()


ers = lcr.query("ERR?")
print(f"error: {ers}")

params = [
"DFMT2", # 1ascii 2BINARY
"FREQ2", # 1 MHz
"AVE=1", # 8 Avg
"CABL1", # 1m cable
"DTIM=0", # delay 0 ms
"HIAC0", # Low accuracy 1 MHz	 (0/1)
"ITIM1", # meas time 1/2/3
"MPAR3", # Cp-G
"OSC=1.0", #OSC level 1.0 V
"RB1", # 1 MHz range 1pF
"OPEN0", # Disable open comp
"SHOR0", # Disable short comp
"STD0", # Disable std comp
"DPAG4", # show status page
"TRIG2", # ext trigger
"VMON0"
]

#lcr.write(";".join(params))


#lrns = lcr.query("*LRN?")

#print(lrns)

def checkErrors():
    ers = lcr.query("ERR?")
    if(int(ers) != 0):
        print(f"error: {ers}")
    
    
checkErrors()

#print(lrns[0:(nchar-1)])
#print(lrns[nchar:(2*nchar-1)])
#print(lrns[(3*nchar):(3*nchar-1)])
#print(lrns[(4*nchar):(4*nchar-1)])

#lcr.write("TRIG1") # Internal trigger
lcr.write("TRIG2") # Manual trigger

maxSize = 30

plt.figure(figsize = (15,8))
plt.xlabel('Time (s)')
plt.ylabel('Cp (F)')

matrixData = np.array([[],[],[]])

print("Starting logging")
lcr.write("DST") # Start continuous reads
endNow = False
nsamp = 0

def handler(signum, frame):
    global endNow
    print("Ctrl-c was pressed. Ending log.")
    endNow = True

signal.signal(signal.SIGINT, handler)
f = open(logfilename,"w")
f.write("t,cp,G\n")
t0 = time.perf_counter()




while not endNow:
	#lcr.write("*TRG")
	#lcr.assert_trigger()
	#v = lcr.read().strip()
	v = lcr.read_binary_values(datatype='d',is_big_endian=True,header_fmt='hp')
	t = time.perf_counter() - t0
	f.write(f"{t:.6f}, {v[0]:.5e},{v[1]:.5e}\n")

	add = np.array([[t],[v[0]],[v[1]]])
	matrixData = np.append(matrixData,add,axis = 1)


	if matrixData.shape[1] >= maxSize*7:
		matrixData = np.delete(matrixData,0,1)	
	
	if (nsamp % 100) == 0:
		print(f"t={t:.3f}")
	nsamp = nsamp + 1
	
	if nsamp >= maxSize:
		plt.cla()
		plt.plot(matrixData[0], matrixData[1])
		plt.xlim(t-maxSize, t)
		#plt.pause(0.0001)



f.close()
duration = time.perf_counter() - t0
lcr.write("DEND")
lcr.write("TRIG1") # Int trigger


print("Logging complete")
print(f"N = {nsamp}")
print(f"T = {duration}")
print(f"Avg Rate = {nsamp/duration}")


lcr.close()
