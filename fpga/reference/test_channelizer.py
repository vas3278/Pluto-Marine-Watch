import unittest
import numpy as np
from channelizer import channelize

class ReferenceTest(unittest.TestCase):
    def test_two_tones(self):
        fs=200000
        n=np.arange(20000)
        x=np.exp(2j*np.pi*25000*n/fs)+0.2*np.exp(-2j*np.pi*25000*n/fs)
        y=channelize(x,fs,0,[25000,-25000],decimation=4,taps=257)
        self.assertAlmostEqual(abs(np.mean(y[25000][100:-100])),1,places=3)
        self.assertAlmostEqual(abs(np.mean(y[-25000][100:-100])),0.2,places=3)
    def test_outside(self):
        with self.assertRaises(ValueError):
            channelize(np.ones(100),200000,0,[100000],decimation=4)
if __name__ == "__main__":
    unittest.main()
