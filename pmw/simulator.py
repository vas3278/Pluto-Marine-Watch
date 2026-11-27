"""Deterministic synthetic navigation; never a live navigation source."""
import math,time
from datetime import datetime,timezone,timedelta
from .navigation import metrics

def move(lat,lon,cog,sog,seconds):
    d=sog*seconds/3600/60; a=math.radians(cog)
    return lat+d*math.cos(a),lon+d*math.sin(a)/math.cos(math.radians(lat))

def sentence(body):
    checksum=0
    for c in body: checksum ^= ord(c)
    return f'${body}*{checksum:02X}'

def coord(v,latitude):
    d=int(abs(v)); m=(abs(v)-d)*60
    return f'{d:0{2 if latitude else 3}d}{m:07.4f}', ('N' if v>=0 else 'S') if latitude else ('E' if v>=0 else 'W')

class Simulator:
    def __init__(self):
        self.start=time.monotonic(); self.epoch=datetime.now(timezone.utc)
    def snapshot(self,elapsed=None):
        t=max(0,time.monotonic()-self.start if elapsed is None else elapsed)
        stamp=self.epoch+timedelta(seconds=t)
        def vessel(name,lat,lon,cog,sog,heading):
            lat,lon=move(lat,lon,cog,sog,t)
            return dict(name=name,position=dict(lat=lat,lon=lon),cog=cog,sog=sog,heading=heading,simulated=True,time=stamp.isoformat())
        own=vessel('DEMO BRAVO',54.45,18.72,87,12.4,84)
        own.update(valid=True,source='simulator')
        targets=[]
        for i,args in enumerate([('DEMO ALPHA',54.47,18.76,220,11,218),('DEMO CHARLIE',54.42,18.75,330,8,332),('DEMO DELTA',54.49,18.69,180,10,181)]):
            target=vessel(*args); target['id']=f'SIM-{i+1}'; target.update(metrics(own,target)); targets.append(target)
        lat,ns=coord(own['position']['lat'],True);lon,ew=coord(own['position']['lon'],False)
        nmea=[sentence(f"GPRMC,{stamp:%H%M%S}.00,A,{lat},{ns},{lon},{ew},{own['sog']:.1f},{own['cog']:.1f},{stamp:%d%m%y},,,A"),sentence(f"HEHDT,{own['heading']:.1f},T")]
        return dict(simulated=True,navigation=own,targets=targets,nmea=nmea)
