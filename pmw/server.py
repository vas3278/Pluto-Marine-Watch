"""Local-only scaffold; no hardware or external network connections."""
import argparse, json, sqlite3, uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
from contextlib import closing

def now(): return datetime.now(timezone.utc).isoformat()

class Store:
    def __init__(self, path):
        self.path = path
        with closing(self.connect()) as db, db:
            db.execute('PRAGMA journal_mode=WAL')
            db.execute('CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, time TEXT NOT NULL, channel INTEGER NOT NULL, frequency_hz INTEGER NOT NULL, sender TEXT, recipient TEXT, text TEXT NOT NULL, status TEXT NOT NULL, simulated INTEGER NOT NULL)')
    def connect(self):
        db=sqlite3.connect(self.path, timeout=10); db.row_factory=sqlite3.Row; return db
    def seed(self):
        with closing(self.connect()) as db, db:
            if db.execute('SELECT COUNT(*) FROM events').fetchone()[0]: return
            db.execute('INSERT INTO events VALUES (?,?,?,?,?,?,?,?,?)',(str(uuid.uuid4()),now(),16,156800000,'DEMO ALPHA','DEMO BRAVO','This is a synthetic test message.','new',1))
    def events(self, channel=None, query=''):
        with closing(self.connect()) as db:
            return [dict(r) for r in db.execute('SELECT * FROM events WHERE (? IS NULL OR channel=?) AND (text LIKE ? OR sender LIKE ? OR recipient LIKE ?) ORDER BY time DESC LIMIT 500',(channel,channel,*(['%'+query+'%']*3)))]
    def status(self, id, status):
        if status not in ('new','reviewed','requires_reply','handled'): raise ValueError('Invalid status')
        with closing(self.connect()) as db, db:
            return db.execute('UPDATE events SET status=? WHERE id=?',(status,id)).rowcount==1

def handler(store, simulator=None):
    class Handler(BaseHTTPRequestHandler):
        def send(self, data, status=200, kind='application/json'):
            body=json.dumps(data,ensure_ascii=False).encode() if kind=='application/json' else data.encode()
            self.send_response(status); self.send_header('Content-Type',kind+'; charset=utf-8'); self.send_header('Content-Length',str(len(body))); self.send_header('Cache-Control','no-store'); self.end_headers(); self.wfile.write(body)
        def do_GET(self):
            p=urlsplit(self.path); q=parse_qs(p.query)
            if p.path=='/': return self.send(Path(__file__).with_name('index.html').read_text(encoding='utf-8'),kind='text/html')
            if p.path=='/api/v1/health': return self.send({'version':'0.0.4','mode':'simulation' if simulator else 'offline','radio':'not_connected','navigation':'simulated' if simulator else 'not_connected','ais':'simulated' if simulator else 'not_connected','asr':'not_connected'})
            if p.path=='/api/v1/simulation': return self.send(simulator.snapshot() if simulator else {'simulated':False})
            if p.path=='/api/v1/navigation' and simulator: return self.send(simulator.snapshot()['navigation'])
            if p.path=='/api/v1/ais/targets' and simulator: return self.send(simulator.snapshot()['targets'])
            if p.path=='/api/v1/navigation': return self.send({'valid':False,'source':None,'position':None,'heading':None,'cog':None,'sog':None})
            if p.path=='/api/v1/ais/targets': return self.send([])
            if p.path=='/api/v1/radio/events':
                try: return self.send(store.events(int(q['channel'][0]) if 'channel' in q else None,q.get('q',[''])[0]))
                except ValueError: return self.send({'error':'invalid channel'},400)
            return self.send({'error':'not found'},404)
        def do_PATCH(self):
            parts=urlsplit(self.path).path.split('/')
            if len(parts)!=7 or parts[1:5]!=['api','v1','radio','events'] or parts[6]!='status': return self.send({'error':'not found'},404)
            try:
                n=int(self.headers.get('Content-Length','0'))
                if not 0<n<=4096: raise ValueError()
                status=json.loads(self.rfile.read(n))['status']; found=store.status(parts[5],status)
                return self.send({'updated':found},200 if found else 404)
            except (ValueError,KeyError,TypeError): return self.send({'error':'invalid request'},400)
    return Handler

def main():
    p=argparse.ArgumentParser(); p.add_argument('--port',type=int,default=8080); p.add_argument('--db',default='data/pmw.sqlite'); p.add_argument('--demo',action='store_true'); a=p.parse_args()
    Path(a.db).parent.mkdir(parents=True,exist_ok=True); s=Store(a.db)
    from .simulator import Simulator
    simulator=Simulator() if a.demo else None
    if a.demo: s.seed()
    print(f'PMW: http://127.0.0.1:{a.port} (simulation only)',flush=True)
    ThreadingHTTPServer(('127.0.0.1',a.port),handler(s, simulator)).serve_forever()
if __name__=='__main__': main()
