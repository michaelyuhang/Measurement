
import csv
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

# TODO limit the size of xs,ys & tpp,vpp

filename = "test.csv"
# amp = 0.145                # TODO - ref_amp is a fix number, detect at the begining
# amp_bias = 0
# freq_bias = 0
# offset_bias = 0            # Since the aliasing issue (lack of datapoints) manual adjustment is needed

global pts
pts = 10

window_cycle = 3
freq_cycle = 0.5            # Sampling length of freq detection
fit_cycle = 0.3             # Sampling length of line fitting (phi detection & ref curve)
offset_cycle = 1            # Sampling length of offset detection
fit_plot_cycle = 0.4

phi_interval =100
offset_interval = 10
amp_interval = 100

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


    n = int(10 * fit_cycle)
    amp_range = np.linspace(0, 2.5, amp_interval)
    a = []
    for i in amp_range:
        fit = 0
        for j in range (0 + fitting_shift, n + fitting_shift):
            dy = ((i * np.sin(2 * math.pi * freq * xs[j] + phi) + offset) - ys[j])**2
        fit = fit + dy
        a.append(fit)
    fit_coeff = min(a)
    amp = amp_range[a.index(fit_coeff)]
    return(amp, fit_coeff)

def fitting (xs, ys, amp_pre, freq, offset_pre, fit_cycle, fitting_shift):           #TODO
    start = int(10 * fitting_shift)
    end = int(10 * (fitting_shift + fit_cycle))
    loc = np.array([])
    fit = []
    phi_range = np.linspace(-math.pi, math.pi, phi_interval)
    offset_range = np.linspace(-0.001, 0.001, offset_interval)
    amp_range = np.linspace(-0.1, 0.1, amp_interval)
    
    for i in phi_range:
        for j in offset_range:
            for k in amp_range:
                fit_coeff = 0
                for l in range(start, end):
                    dy = ((k + amp_pre) * np.sin(2 * math.pi * freq * xs[l] + i) + (offset_pre + j) - ys[l])**2
                    fit_coeff = fit_coeff + dy
                fit.append(fit_coeff)
                kji = [k, j, i]
                loc = np.append(loc, kji, axis = 0)
    print("\n")
    
    fit_optm = min(fit)
    fit_optm_indices = fit.index(fit_optm)
    
    print(fit_optm, fit_optm_indices)

    amp = loc[3 * fit_optm_indices] + amp_pre
    off = loc[1 + 3 * fit_optm_indices] +offset_pre
    phi = loc[2 + 3 * fit_optm_indices]
    return(amp, off, phi)


# =======================================================
# MAIN
# =======================================================

iteration = 0
fitting_shift = 0

xs,ys = getEntireWaveform(filename)
xs_window = []
ys_window = []
for i in range (iteration, int(pts * window_cycle + iteration)):
    xs_window.append(xs[i])
    ys_window.append(ys[i])

x_interp = np.linspace(min(xs_window), max(xs_window), window_cycle * 100)
y_cubic = interp1d(xs_window, ys_window, kind= "cubic")

x_top, y_top = getInterpMin(x_interp, y_cubic(x_interp))
x_bot, y_bot = getInterpMax(x_interp, y_cubic(x_interp))


# ========================================================
# Get initial parameters
# ========================================================
amp_init = abs(y_top[0] - y_bot[0])/2
freq_init = getFreq(xs_window, freq_cycle, fitting_shift)
offset_init = getOffset(ys_window, offset_cycle, fitting_shift)


# ========================================================
# Curve fitting
# ========================================================

# phi, phi_fit = fitPhi(x_interp, y_cubic(x_interp), offset_, phi_interval, fitting_shift)
# print(phi, phi_fit)

# offset, offset_fit = fitOffset (x_interp, y_cubic(x_interp), phi, offset_interval, fitting_shift)
# print(offset, offset_fit)

# amp, amp_fit = fitAmp (x_interp, y_cubic(x_interp), phi, offset_est, amp_interval, fitting_shift)
# print(amp, amp_fit)
amp, offset, phi = fitting(xs_window, ys_window, amp_init, freq_init, offset_init, fit_cycle, fitting_shift)

print(amp_init, freq_init, offset_init)
print("\n")
print(amp, freq_init, offset, phi)

# ========================================================
# Fit offset
# ========================================================

# print(amp)
# print(freq)
# print(phi, phi_fit)
# print(offset, offset_fit)

# ========================================================
# Plot the rolling fitting curve
# ========================================================
xs_ref = np.linspace(xs_window[0 + fitting_shift],xs_window[int(pts * fit_plot_cycle) + fitting_shift],int(fit_plot_cycle *50))
ref = []
ref = amp * np.sin(2 * math.pi * freq_init * xs_ref + phi) + offset

fig, ax = plt.subplots(figsize = (15,8))
ax.plot(xs_window, ys_window, "x",)
ax.plot(x_interp, y_cubic(x_interp),"red", label = "cubic")
# ax.plot(x_interp, y_quad(x_interp),"blue", label = "quad")

ax.plot(x_top, y_top, "o")
ax.plot(x_bot, y_bot, "o")

ax.plot(xs_ref, ref, "blue")

plt.xticks(rotation=45, ha='right')
plt.grid()
plt.show()
plt.pause(0.01)
