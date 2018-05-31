from numpy import diff
#====================================== DERIVATIVE AND ADAPTIVE FILTERING ==============================================
# Formula : H(z) = 0.1*(2+z^-1 - z^-2 - z^-3) #Five point derivative
def derivative(raw_signal):
    der = diff(raw_signal)
    return der

def five_point_derivative(raw_signal):
    ecg_der = []
    for i in xrange(len(raw_signal)):
        der = 0.1 * 2 * (raw_signal[i] + raw_signal[i-1] - raw_signal[i-3] - raw_signal[i-4])
        ecg_der.append(der)

    return ecg_der

def adaptive_filter(ecg_der):
    ecg_adp = []; a = 0.95;
    ecg_adp.append(0.01);
    for i in xrange(len(ecg_der)):
            adp = ( a * ecg_adp[i-1] ) + ( (1 - a) * ecg_der[i])
            ecg_adp.append(adp)
    return ecg_adp

# def low_pass_filter():
#     H = (1 - z**-6)**2 / (1 - z**-1)**2
#     y[n] = 2 y[n-1] - y[n-2] + x[n] - 2 x[n-6] + x[n-12]
#     Where the cutoff frequency is about 11 Hz and the gain is 36.
#====================================== BANDPASS & BUTTERWORTH FILTERING ===============================================
from scipy.signal import butter, lfilter

def butter_bandpass_filter(data, lowcut = 5, highcut = 15, fs = 360, order = 6):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq

    b, a = butter(order, [low, high], btype='band', analog=False)
    y = lfilter(b, a, data)
    return y

# ___________________________________SQUARING FUNCTION____________________________________________________________________

def squaring(data):
    squared = []
    for i in range(len(data)):
        data[i] = data[i] ** 2
        squared.append(data[i])
    return squared
