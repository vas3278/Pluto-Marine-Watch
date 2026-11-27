"""Local tangent-plane estimates for simulation, not certified navigation."""
import math

def metrics(own, target):
    a,b=own['position'],target['position']
    north=(b['lat']-a['lat'])*60
    east=((b['lon']-a['lon']+180)%360-180)*60*math.cos(math.radians((a['lat']+b['lat'])/2))
    def velocity(v):
        c=math.radians(v['cog']); return v['sog']*math.sin(c),v['sog']*math.cos(c)
    oe,on=velocity(own); te,tn=velocity(target); ve,vn=te-oe,tn-on
    speed2=ve*ve+vn*vn
    t=-(east*ve+north*vn)/speed2 if speed2>1e-12 else None
    future=max(0,t) if t is not None else 0
    distance=math.hypot(east,north)
    bearing=math.degrees(math.atan2(east,north))%360 if distance>1e-9 else None
    return dict(east_nm=east,north_nm=north,distance_nm=distance,bearing_deg=bearing,relative_bearing_deg=(bearing-own['heading'])%360 if bearing is not None else None,cpa_nm=math.hypot(east+ve*future,north+vn*future),tcpa_min=t*60 if t is not None else None)
