import unittest
from pmw.nmea import parse,Receiver
from pmw.simulator import sentence

class NmeaTests(unittest.TestCase):
    def test_rmc(self):
        d=parse(sentence('GPRMC,120000,A,5400.000,N,01830.000,E,12.0,90.0,271126,,,A'))
        self.assertEqual(d['position'],{'lat':54,'lon':18.5})
        self.assertEqual(d['sog'],12)
    def test_heading(self):
        self.assertEqual(parse(sentence('HEHDT,123.4,T')),{'heading':123.4})
        self.assertEqual(parse(sentence('HCHDG,123.4,,,,')),{'magnetic_heading':123.4})
    def test_checksum(self):
        with self.assertRaises(ValueError):parse('$HEHDT,123.4,T*00')
    def test_stale(self):
        r=Receiver('udp://127.0.0.1:10110',ttl=-1)
        r.feed(sentence('HEHDT,123.4,T'))
        self.assertIsNone(r.snapshot()['heading'])
    def test_invalid_fix(self):
        r=Receiver('tcp://127.0.0.1:10110')
        r.feed(sentence('GPRMC,120000,A,5400.000,N,01830.000,E,12.0,90.0,271126,,,A'))
        self.assertTrue(r.snapshot()['valid'])
        r.feed(sentence('GPRMC,120001,V'))
        self.assertFalse(r.snapshot()['valid'])
