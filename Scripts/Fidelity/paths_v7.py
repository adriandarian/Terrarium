"""Continuous-distance earth tracks, independent of traced vertex density."""
import bisect
import math
import random
import reference as ref
from placement import place_xyz


def sample_track(points, spacing=155):
    """Yield midpoint, tangent and coverage length at uniform arc distances.

    Traces can contain dense smoothing samples or duplicate landmarks without
    producing tiny compressed tile strips. Endpoints are covered by half tiles.
    """
    if spacing <= 0:
        raise ValueError('Track spacing must be positive')
    clean=[]
    cumulative=[0.0]
    for point in points:
        if not clean:
            clean.append(point)
        else:
            distance=math.hypot(point[0]-clean[-1][0],point[1]-clean[-1][1])
            if distance > 1e-6:
                clean.append(point)
                cumulative.append(cumulative[-1]+distance)
    if len(clean)<2:
        return
    total=cumulative[-1]
    count=max(1,math.ceil(total/spacing))
    step=total/count

    def at(distance):
        distance=max(0,min(total,distance))
        index=min(len(clean)-2,bisect.bisect_right(cumulative,distance)-1)
        t=(distance-cumulative[index])/(cumulative[index+1]-cumulative[index])
        a,b=clean[index],clean[index+1]
        return (a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t)

    for index in range(count):
        distance=(index+.5)*step
        center=at(distance)
        before,after=at(distance-step*.35),at(distance+step*.35)
        yaw=math.degrees(math.atan2(after[1]-before[1],after[0]-before[0]))
        yield center,yaw,step


def build():
    rng=random.Random(8087)
    for height,path,width in ref.PATHS:
        points=[ref.world(*point,height) for point in path]
        for center,yaw,length in sample_track(points):
            # Longitudinal overlap hides ends; alternating orientations vary the
            # asymmetrical soil lobes. No offset changes the traced route itself.
            yaw+=180 if rng.random()<.5 else 0
            place_xyz('PathTile_v4',(*center,height+11+rng.uniform(-.12,.12)),
                      (length/188,width/200*rng.uniform(.98,1.025),.65),yaw,'Paths')
    # Preserve original stair and bridge anchor transforms exactly.
    yaw=2
    r=math.radians(yaw)
    sx,sy,sz=1,.75,280/249
    top=ref.world(157,429,560)
    offset=(-math.sin(r)*147*sy,math.cos(r)*147*sy,249*sz)
    place_xyz('StoneStairs_v3',tuple(top[i]-offset[i] for i in range(3)),
              (sx,sy,sz),yaw,'Stairs',False)
    deck=ref.world(306,579,280)
    place_xyz('PlankBridge_v4',(deck[0],deck[1],deck[2]-58),(.9,1.4,1),-4,'Bridge',False)
