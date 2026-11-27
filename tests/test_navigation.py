import unittest
from pmw.navigation import metrics

def vessel(lat,lon,cog,sog,heading=0):
    return dict(position=dict(lat=lat,lon=lon),cog=cog,sog=sog,heading=heading)

class NavigationTests(unittest.TestCase):
    def test_head_on(self):
        m=metrics(vessel(0,0,0,10),vessel(1/60,0,180,10))
        self.assertAlmostEqual(m['cpa_nm'],0); self.assertAlmostEqual(m['tcpa_min'],3)
    def test_receding(self):
        m=metrics(vessel(0,0,180,10),vessel(1/60,0,0,10))
        self.assertLess(m['tcpa_min'],0); self.assertAlmostEqual(m['cpa_nm'],1)
    def test_parallel(self):
        m=metrics(vessel(0,0,0,10,90),vessel(1/60,0,0,10))
        self.assertIsNone(m['tcpa_min']); self.assertAlmostEqual(m['relative_bearing_deg'],270)
