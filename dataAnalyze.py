
import csv
import math
import numpy as np
import matplotlib.pyplot as plt

filename = "test.csv"
freq = 1e5                  #todo - to detect (amp doesn't change thrughout the measurement) need to verify

amp = 0.1424                #todo - to detect (amp doesn't change thrughout the measurement) need to verify
offset_bias = -0.004
ave = 1
pts = 10

ref_cycle = 1
offset_cycle = 1

def getEntireWaveform (filename):
    xs = []
    ys = []
    with open(filename, mode = 'r') as file_obj:
        # Create reader object by passing the file  
        # object to reader method 
        reader_obj = csv.reader(file_obj)
        for row in file_obj:
            x, y =row.split(',')
            xs.append(float(x))
            ys.append(float(y))
    return(xs, ys)

def getPk2Pk (filename):
    with open(filename, mode = 'r') as file_obj:
        # Create reader object by passing the file  
        # object to reader method 
        reader_obj = csv.reader(file_obj)

        temp_ts = []
        temp_vs = []
        tpp = []
        vpp = []
    
        rowNum = 0
        for row in file_obj:
            t,v = row.split(',')
       
            temp_ts.append(float(t))
            temp_vs.append(float(v))
        
            if (rowNum + 1) == 10:
                hi = max(temp_vs)
                tHi = temp_vs.index(hi)
                lo = min(temp_vs)
                tLo = temp_vs.index(lo)
        
                if tHi < tLo:
                    waveSign = "sine"
                    tpp.append(temp_ts[tHi])
                    vpp.append(hi)
                
                    tpp.append(temp_ts[tLo])
                    vpp.append(lo)
                
                else:
                    waveSign = "cosine"
                    tpp.append(temp_ts[tLo])
                    vpp.append(lo)
                
                    tpp.append(temp_ts[tHi])
                    vpp.append(hi)
                
                temp_vs = []
                temp_ts = []
            
            elif (rowNum + 1) % 10 == 0:
                hi = max(temp_vs)
                tHi = temp_vs.index(hi)
                lo = min(temp_vs)
                tLo = temp_vs.index(lo)
                
                if waveSign == "sine":
                    tpp.append(temp_ts[tHi])
                    vpp.append(hi)
                    
                    tpp.append(temp_ts[tLo])
                    vpp.append(lo)
                    
                else:
                    tpp.append(temp_ts[tLo])
                    vpp.append(lo)
                    
                    tpp.append(temp_ts[tHi])
                    vpp.append(hi)
                    
                temp_vs = []
                temp_ts = []
            rowNum = rowNum + 1
    return(tpp,vpp)

def getOffset (ys, cycle):
    offset = 0
    length = range(0, 10 * cycle)
    for i in length:
        offset = offset + ys[i]
    return(offset/10/cycle)

# def getLocalFreq(xs, ys ,cycle):
#     length = range(0, 10 * cycle)
#     for i in length:
    

xs,ys = getEntireWaveform(filename)

# amplitude = abs(ys[1]-ys[2])
offset = getOffset(ys,offset_cycle)
offset = offset + offset_bias #todo

ys_zero = [y - offset for y in ys]

print(amp)
print(offset)

xs_ref = np.linspace(xs[0],xs[9 * ref_cycle- 1],ref_cycle *50)

phi = -0.0000026                                        #todo

ref = []
ref = amp * np.sin(2 * math.pi * freq * (xs_ref+phi))   #todo detect amp & freq & phi

fig, ax = plt.subplots()
ax.plot(xs,ys_zero,"x",)
# ax.plot(xs_ref, ref,"x")
ax.plot(xs_ref, ref)

plt.xticks(rotation=45, ha='right')
plt.grid()
plt.show()

# todo calculate the difference between sig_mea and sig_ref (back calculate the delta(phi) from the (y_mea - y_ref))

