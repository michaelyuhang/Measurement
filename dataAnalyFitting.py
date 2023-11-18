
import csv
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

# TODO limit the size of xs,ys & tpp,vpp

filename = "test1.csv"

global pts
pts = 10

freq_cycle = 0.5            # Sampling length of intitial freq detection
offset_cycle = 1            # Sampling length of intial offset detection

fit_cycle = 1             # Sampling length of line fitting (phi detection & ref curve)

fit_plot_cycle = 1

phi_interval =1000
offset_interval = 1000
amp_interval = 1000

# ========================================================
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

def getPk2Pk (xs, ys):                                      # Not using

    temp_ts = []
    temp_vs = []
    tpp = []
    vpp = []

    rowNum = 0
    for i in range (0, len(xs)):
        t,v = xs[i], ys[i]
    
        temp_ts.append(t)
        temp_vs.append(v)
    
        if (rowNum + 1) == pts:
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
        
        elif (rowNum + 1) % pts == 0:
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
    return(tpp, vpp, waveSign)

    return

def getInterpMax (x_interp, y_interp):
    
    local_max_indices = np.where((np.diff(np.sign(np.diff(y_interp))) < 0) & (y_interp[1:-1] > 0))[0] + 1
    local_max_x = x_interp[local_max_indices]
    local_max_y = y_interp[local_max_indices]
    
    return(local_max_x, local_max_y)

def getInterpMin (x_interp, y_interp):
    
    local_min_indices = np.where((np.diff(np.sign(np.diff(y_interp))) > 0) & (y_interp[1:-1] < 0))[0] + 1
    local_min_x = x_interp[local_min_indices]
    local_min_y = y_interp[local_min_indices]
    
    return(local_min_x, local_min_y)

def getFreq (xs, n, fitting_shift):
    deltaT = xs[int(pts * n + fitting_shift)] - xs[fitting_shift]
    Freq = n / deltaT
    
    return(Freq)

def getOffset (ys, n, fitting_shift):
    offset = 0
    length = range(fitting_shift, int(pts * n + fitting_shift))
    for i in length:
        offset = offset + ys[i]
    return(offset / pts / n)

def getPhi (x_range, y_range, amp, freq, phi_interval):
    fitting_coeff = []
    phi_range = np.linspace(0, -1/freq ,phi_interval)
    for i in phi_range:
        ref = amp * np.sin(2 * math.pi * freq * (x_range + i))
        
        a = 0
        for i in range (0, len(ref)):
            a = a + (ref[i] - y_range[i]) ** 2
        
        fitting_coeff.append(a)
    fit = min(fitting_coeff)
    phi = phi_range[fitting_coeff.index(fit)]    
    return(phi, fit)

def fitPhi (xs, y_interp, amp, freq, offset_local, phi_interval, fitting_shift):
    start = xs[int(10 * fitting_shift)]
    end = xs[int(10 * (fitting_shift + fit_cycle))]
    x_interp = np.linspace(start, end, int(20 * fit_cycle))
    phi_range = np.linspace(-math.pi, math.pi, phi_interval)
    a = []
    for i in phi_range:
        fit = 0
        for j in x_interp:
            dy = ((amp * np.sin(2 * math.pi * freq * j + i) + offset_local) - y_interp(j))**2
            fit = fit + dy
        a.append(fit)
    fit_coeff = min(a)
    phi = phi_range[a.index(fit_coeff)]
    return (phi, fit_coeff)

def fitOffset (xs, y_interp, amp, freq, phi, offset_interval, fitting_shift):
    start = xs[int(10 * fitting_shift)]
    end = xs[int(10 * (fitting_shift + fit_cycle))]
    x_interp = np.linspace(start, end, int(20 * fit_cycle))
    offset_range = np.linspace(-0.1, 0.1, offset_interval)
    a = []
    for i in offset_range:
        fit = 0
        for j in x_interp:
            dy = ((amp * np.sin(2 * math.pi * freq * j + phi) + i) - y_interp(j))**2
            fit = fit + dy
        a.append(fit)
    fit_coeff = min(a)
    offset = offset_range[a.index(fit_coeff)]
    return(offset, fit_coeff)

def fitAmp (xs, y_interp, amp, freq, phi, offset, amp_interval, fitting_shift):
    start = xs[int(10 * fitting_shift)]
    end = xs[int(10 * (fitting_shift + fit_cycle))]
    x_interp = np.linspace(start, end, int(20 * fit_cycle))
    amp_range = np.linspace(-0.1, 0.1, amp_interval)
    a = []
    for i in amp_range:
        fit = 0
        for j in x_interp:
            dy = (((amp+i) * np.sin(2 * math.pi * freq * j + phi) + offset) - y_interp(j))**2

            fit = fit + dy
        a.append(fit)
    fit_coeff = min(a)
    amp = amp + amp_range[a.index(fit_coeff)]
    return(amp, fit_coeff)

# =================================================================
# MAIN
# =================================================================

aquisition_iteration = 2
aquisition_numPts = 2000

# =================================================================
# Get data
# =================================================================
xs = []
ys = []
xs,ys = getEntireWaveform(filename)

result_amp = []
result_phi = []
result_fit = []

for iteration in range(0, aquisition_iteration):
    
    # Select valid data points from their time windows. Jumping from
    # the current iteration to next iteration
    
    xs_window = []
    ys_window = []
    for i in range (int(aquisition_numPts * iteration), aquisition_numPts * (iteration + 1)-1):     #double check with new aqusistion
        xs_window.append(xs[i])
        ys_window.append(ys[i])

    x_interp = np.linspace(min(xs_window), max(xs_window), aquisition_numPts * 10)
    y_cubic = interp1d(xs_window, ys_window, kind= "cubic")
    # y_quad = interp1d(xs_window, ys_window, kind= "quadratic")

    # tpp, vpp, wave = getPk2Pk(xs_window, ys_window)
    x_top, y_top = getInterpMin(x_interp, y_cubic(x_interp))
    x_bot, y_bot = getInterpMax(x_interp, y_cubic(x_interp))

    # ==================================================================
    # Get initial parameters
    # ==================================================================

    amp_init = abs(y_top[0] - y_bot[0])/2
    freq_init = getFreq(xs_window, freq_cycle, 0)
    offset_init = getOffset(ys_window, offset_cycle, 0)
    
    print(amp_init, freq_init, offset_init)


    # ==================================================================
    # Curve fitting
    # ==================================================================
    fitting_shift = 0
    
    while fitting_shift + 10 * max([freq_cycle, fit_cycle, offset_cycle, fit_plot_cycle]) < aquisition_numPts:

        phi, phi_fit = fitPhi(x_interp, y_cubic, amp_init, freq_init, offset_init, phi_interval, fitting_shift)
        # print(phi, phi_fit)

        offset_init, offset_fit = fitOffset (x_interp, y_cubic, amp_init, freq_init, phi, offset_interval, fitting_shift)
        # print(offset_init, offset_fit)

        amp_init, amp_fit = fitAmp (x_interp, y_cubic, amp_init, freq_init, phi, offset_init, amp_interval, fitting_shift)
        # print(amp_init, amp_fit)


        # print(phi, amp_init, offset_init, amp_fit)

        # # ==================================================================
        # # Plot the rolling fitting curve
        # # ==================================================================
        # xs_ref = np.linspace(xs_window[fitting_shift], xs_window[int(pts * fit_plot_cycle + fitting_shift)],int(fit_plot_cycle *100))
        # ref = []
        # ref = amp_init * np.sin(2 * math.pi * freq_init * xs_ref + phi) + offset_init

        # fig, ax = plt.subplots(figsize = (15,8))
        # ax.plot(xs_window, ys_window, "x")
        # ax.plot(x_interp, y_cubic(x_interp),"red", label = "cubic")
        # # ax.plot(x_interp, y_quad(x_interp),"blue", label = "quad")

        # ax.plot(x_top, y_top, "o")
        # ax.plot(x_bot, y_bot, "o")

        # ax.plot(xs_ref, ref, "blue")

        # plt.xticks(rotation=45, ha='right')
        # plt.grid()
        # plt.show()
        # plt.pause(0.01)
        # plt.close('all')

        fitting_shift = fitting_shift +1
        print(fitting_shift, iteration)

        result_amp.append(amp_init)
        result_phi.append(phi)
        result_fit.append(amp_fit)
        
    
    fig, ax = plt.subplots(3,1, figsize = (15,8))
    ax[0].plot(xs_window[0:len(result_amp)], result_amp)
    ax[1].plot(xs_window[0:len(result_phi)], result_phi)
    ax[2].plot(xs_window[0:len(result_fit)], result_fit)


    plt.show()
    plt.pause(0.01)