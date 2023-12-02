import pyvisa
import time
import signal
import numpy as np
import matplotlib.pyplot as plt

logfilename = "out.csv"

maxSize = 30

plt.figure(figsize = (15,8))
plt.xlabel('Time (s)')
plt.ylabel('Cp (F)')

matrixData = np.array([[],[],[]])


def handler(signum, frame):
    global endNow
    print("Ctrl-c was pressed. Ending log.")
    endNow = True


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
