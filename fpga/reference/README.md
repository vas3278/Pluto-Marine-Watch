# DSP reference models
channelizer.py: independent DDC oracle.
pfb.py: oversampled polyphase FFT bank, 512 bins, hop 256, 12 taps per bin, 12.8 MS/s, 25 kHz bin spacing and 50 kS/s output. Output time indices refer to FIR window centers; phase referenced to input sample zero. Offline only. For 12.5 kHz spacing evaluate 1024 bins with hop 256 or 512 and suitable filter design. Adjacent-channel rejection and fixed-point performance are not yet established.
Run: python -m pip install -r fpga/reference/requirements.txt
Then: python -m unittest discover -s fpga/reference -v
The engineering grid is not an authoritative regional allocation table. Do not label every grid point as an assigned marine channel.
