import unittest,tempfile,threading,json,urllib.request
from pathlib import Path
from http.server import ThreadingHTTPServer
from pmw.simulator import Simulator,move,sentence
from pmw.server import Store,handler
class SimulationTests(unittest.TestCase):
 def test_motion(self):
  s=Simulator();a=s.snapshot(0);b=s.snapshot(3600)
  self.assertNotEqual(a['navigation']['position'],b['navigation']['position']);self.assertEqual(len(b['targets']),3);self.assertTrue(all(t['simulated'] for t in b['targets']));self.assertEqual(a['navigation']['heading'],84)
 def test_checksum(self):
  self.assertEqual(sentence('HEHDT,123.4,T'),'$HEHDT,123.4,T*2B')
 def test_http_simulation(self):
  with tempfile.TemporaryDirectory() as d:
   server=ThreadingHTTPServer(('127.0.0.1',0),handler(Store(Path(d)/'db'),Simulator()));t=threading.Thread(target=server.serve_forever);t.start()
   try:
    def get(p):
     with urllib.request.urlopen(f'http://127.0.0.1:{server.server_port}/api/v1/'+p) as r:return json.load(r)
    self.assertTrue(get('simulation')['simulated']);self.assertTrue(get('navigation')['valid']);self.assertEqual(len(get('ais/targets')),3);self.assertEqual(get('health')['ais'],'simulated')
   finally:server.shutdown();t.join();server.server_close()
