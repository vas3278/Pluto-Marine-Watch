import unittest
from protocol.framing import encode, decode, PREFIX

class FramingTests(unittest.TestCase):
    def test_roundtrip(self):
        h,p=decode(encode({"type":"AUDIO","channel":"16"},b"\x00\xff"))
        self.assertEqual(h["channel"],"16")
        self.assertEqual(p,b"\x00\xff")
    def test_corruption(self):
        f=encode({},b"abc")
        with self.assertRaises(ValueError):
            decode(f[:-1]+b"x")
    def test_truncated(self):
        with self.assertRaises(ValueError):
            decode(encode({},b"abc")[:-1])
    def test_limit(self):
        with self.assertRaises(ValueError):
            decode(PREFIX.pack(b"PMW1",16385,0))
