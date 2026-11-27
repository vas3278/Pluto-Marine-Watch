"""Floating-point reference for an oversampled DDC filter bank; not FPGA RTL."""
import numpy as np
from scipy.signal import firwin, upfirdn

def channelize(iq, sample_rate, center_hz, frequencies, decimation=256, taps=2049, cutoff_hz=10000):
    """Offline reference, returns complex baseband per physical frequency.
    Output rate = sample_rate/decimation; includes FIR transient.
    """
    iq = np.asarray(iq, dtype=np.complex128)
    if iq.ndim != 1 or sample_rate <= 0 or decimation < 1 or taps < 3:
        raise ValueError("invalid input")
    if not 0 < cutoff_hz < sample_rate / (2 * decimation):
        raise ValueError("invalid cutoff")
    h = firwin(taps, cutoff_hz, fs=sample_rate)
    n = np.arange(iq.size)
    out = {}
    for f in set(frequencies):
        offset = f - center_hz
        if abs(offset) + cutoff_hz >= sample_rate / 2:
            raise ValueError("frequency outside capture")
        out[f] = upfirdn(h, iq * np.exp(-2j*np.pi*offset*n/sample_rate), down=decimation)
    return out
