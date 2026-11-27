import unittest,tempfile,threading,json,urllib.request
from pathlib import Path
from http.server import ThreadingHTTPServer
from pmw.server import Store,handler
class Test(unittest.TestCase):
 def test_store(self):
  with tempfile.TemporaryDirectory() as d:
   s=Store(Path(d)/'db');s.seed();s.seed();rows=s.events(16,'synthetic');self.assertEqual(len(rows),1);self.assertEqual(s.events(13),[]);self.assertTrue(s.status(rows[0]['id'],'reviewed'));self.assertEqual(s.events()[0]['status'],'reviewed');self.assertRaises(ValueError,s.status,rows[0]['id'],'bad')
 def test_http(self):
  with tempfile.TemporaryDirectory() as d:
   s=Store(Path(d)/'db');s.seed();server=ThreadingHTTPServer(('127.0.0.1',0),handler(s));t=threading.Thread(target=server.serve_forever);t.start()
   try:
    base=f'http://127.0.0.1:{server.server_port}';get=lambda p:json.load(urllib.request.urlopen(base+p));self.assertEqual(get('/api/v1/health')['radio'],'not_connected');self.assertFalse(get('/api/v1/navigation')['valid']);self.assertEqual(get('/api/v1/ais/targets'),[]);row=get('/api/v1/radio/events')[0];req=urllib.request.Request(base+'/api/v1/radio/events/'+row['id']+'/status',data=b'{"status":"handled"}',method='PATCH');self.assertTrue(json.load(urllib.request.urlopen(req))['updated']);self.assertEqual(get('/api/v1/radio/events')[0]['status'],'handled');self.assertIn(b'Pluto Marine Watch',urllib.request.urlopen(base+'/').read())
   finally:server.shutdown();t.join();server.server_close()
