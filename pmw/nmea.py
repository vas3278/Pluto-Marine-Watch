"""Read-only NMEA 0183 input. No commands are sent to the gateway."""
import math, socket, threading, time
from datetime import datetime, timezone
from urllib.parse import urlsplit

def number(value, low, high):
    n=float(value)
    if not math.isfinite(n) or not low <= n <= high: raise ValueError('range')
    return n

def coordinate(value, hemisphere, latitude):
    n=number(value,0,18060); d=int(n//100); m=n-d*100
    if m>=60 or hemisphere not in ('NS' if latitude else 'EW'): raise ValueError('coordinate')
    return number((d+m/60)*(-1 if hemisphere in 'SW' else 1),-90 if latitude else -180,90 if latitude else 180)

def parse(line):
    if len(line)>1024 or not line.startswith(('$','!')): raise ValueError('frame')
    body,check=line[1:].rsplit('*',1)
    c=0
    for ch in body: c ^= ord(ch)
    if len(check)!=2 or c!=int(check,16): raise ValueError('checksum')
    f=body.split(','); kind=f[0][-3:]
    if kind=='RMC':
        if f[2]!='A': return {'position':None,'cog':None,'sog':None}
        return dict(position=dict(lat=coordinate(f[3],f[4],True),lon=coordinate(f[5],f[6],False)),sog=number(f[7],0,200),cog=number(f[8],0,360)%360)
    if kind=='GGA':
        if int(f[6])<=0:return {'position':None}
        return dict(position=dict(lat=coordinate(f[2],f[3],True),lon=coordinate(f[4],f[5],False)))
    if kind=='HDT' and f[2]=='T': return {'heading':number(f[1],0,360)%360}
    if kind=='HDG': return {'magnetic_heading':number(f[1],0,360)%360}
    if kind=='VTG':
        if len(f)>9 and f[9]=='N':return {'cog':None,'sog':None}
        if f[2]!='T' or f[6]!='N':raise ValueError('units')
        return {'cog':number(f[1],0,360)%360,'sog':number(f[5],0,200)}
    return {}

class Receiver:
    def __init__(self,url,ttl=15):
        u=urlsplit(url)
        if u.scheme not in ('tcp','udp') or not u.hostname or not u.port or u.path or u.query or u.username:raise ValueError('use tcp://host:port or udp://bind-address:port')
        self.scheme,self.host,self.port=u.scheme,u.hostname,u.port
        self.ttl=ttl; self.lock=threading.Lock();self.stop=threading.Event();self.fields={};self.state='starting';self.accepted=0;self.rejected=0
    def feed(self,line):
        try: fields=parse(line.strip())
        except (ValueError,IndexError,OverflowError):
            with self.lock:self.rejected+=1
            return
        with self.lock:
            self.accepted+=1
            for k,v in fields.items():self.fields[k]=(v,time.monotonic())
    def snapshot(self):
        with self.lock:
            now=time.monotonic()
            data={k:(self.fields[k][0] if k in self.fields and now-self.fields[k][1]<=self.ttl else None) for k in ('position','heading','magnetic_heading','cog','sog')}
            data.update(valid=data['position'] is not None,source='nmea0183',simulated=False,connection=self.state,accepted=self.accepted,rejected=self.rejected)
            return data
    def run(self):
        while not self.stop.is_set():
            try:
                with (socket.create_connection((self.host,self.port),timeout=2) if self.scheme=='tcp' else socket.socket(socket.AF_INET,socket.SOCK_DGRAM)) as s:
                    if self.scheme=='udp':s.bind((self.host,self.port))
                    s.settimeout(1)
                    with self.lock:self.state='receiving'
                    buf=b''
                    while not self.stop.is_set():
                        try: chunk=s.recv(8192)
                        except socket.timeout:continue
                        if self.scheme=='tcp' and not chunk:break
                        if self.scheme=='udp':
                            for line in chunk.splitlines():self.feed(line.decode('ascii','replace'))
                        else:
                            buf+=chunk
                            while b'\n' in buf:
                                line,buf=buf.split(b'\n',1);self.feed(line.decode('ascii','replace'))
                            if len(buf)>4096:buf=b''
            except OSError:pass
            with self.lock:self.state='disconnected'
            self.stop.wait(1)
