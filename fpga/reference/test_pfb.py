import unittest
import numpy as np
from pfb import analyze

class PFBTests(unittest.TestCase):
    def test_two_bins(self):
        fs=12800000
        n=np.arange(32768)
        x=np.exp(2j*np.pi*250000*n/fs)+0.2*np.exp(-2j*np.pi*500000*n/fs)
        f,t,y=analyze(x)
        a=np.argmin(abs(f-250000))
        b=np.argmin(abs(f+500000))
        self.assertAlmostEqual(abs(y[:,a].mean()),1,places=3)
        self.assertAlmostEqual(abs(y[:,b].mean()),0.2,places=3)
        self.assertEqual(y.shape[1],512)
        self.assertTrue(np.all(np.diff(t)==256))
    def test_short(self):
        f,t,y=analyze(np.zeros(100))
        self.assertEqual(y.shape,(0,512))
    def test_phase(self):
        n=np.arange(16384)
        f,t,y=analyze(np.exp(2j*np.pi*25000*n/12800000))
        self.assertLess(np.max(abs(y[:,1]-1)),1e-8)
