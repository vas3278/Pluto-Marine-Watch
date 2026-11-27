"""Offline oversampled polyphase DFT analysis bank, complex input.
Output bins follow numpy.fft.fftfreq. No fixed-point or streaming RTL.
"""
import numpy as np
from scipy.signal import firwin

def analyze(iq, fs=12800000, bins=512, hop=256, taps_per_bin=12, cutoff=10000):
    x=np.asarray(iq,dtype=np.complex128)
    if x.ndim!=1 or bins<2 or not 0<hop<=bins or taps_per_bin<2 or not 0<cutoff<fs/2:
        raise ValueError("invalid configuration")
    length=bins*taps_per_bin
    h=firwin(length,cutoff,fs=fs)
    offsets=np.arange(length)
    starts=np.arange(0,max(0,len(x)-length+1),hop)
    result=np.empty((len(starts),bins),dtype=np.complex128)
    k=np.arange(bins)
    for i,s in enumerate(starts):
        poly=(x[s:s+length]*h).reshape(taps_per_bin,bins).sum(axis=0)
        result[i]=np.fft.fft(poly)*np.exp(-2j*np.pi*k*(s%bins)/bins)
    return np.fft.fftfreq(bins,1/fs),starts+(length-1)/2,result
