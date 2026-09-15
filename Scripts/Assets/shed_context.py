"""Preserve the blue shed while placing its attached trough beside the left wall."""
from meshkit import Mesh,sub,cross,dot
import shed_v2,detail_enrichment

def build():
    save=Mesh.save
    try:
        Mesh.save=lambda self:self
        m=shed_v2.build()
    finally:Mesh.save=save
    detail_enrichment.enrich(m)
    for part in m.parts:
        cx,cy,cz=part['center']
        ids={i for t in m.triangles[part['first']:part['end']] for i in t}
        if cy < -128 and cz<70:
            # Rotate the trough and its water/boards together, leaving the door open.
            for i in ids:
                x,y,z=m.vertices[i];m.vertices[i]=(150-(y+158),14+x,z)
        elif cz<35 and ((cx>105 and cy<0) or (cx<-105 and cy>35)):
            # Keep the original footing rocks, arranged on the doorway's right.
            for i in ids:
                x,y,z=m.vertices[i];m.vertices[i]=(x-2*cx,y,z)
        elif cx < -100 and -20<cy<50 and cz<65:
            # Barrel is tucked at the back instead of filling the clear approach.
            for i in ids:
                x,y,z=m.vertices[i];m.vertices[i]=(x+5,y+90,z)
        tris=m.triangles[part['first']:part['end']]
        center=tuple(sum(m.vertices[i][a] for i in ids)/len(ids) for a in range(3))
        part['center']=center
        part['volume']=sum(dot(sub(m.vertices[t[0]],center),cross(sub(m.vertices[t[1]],center),sub(m.vertices[t[2]],center)))/6 for t in tris)
        assert part['volume']>0
    m.name='SM_Shed_Context_Reference';m.revises='SM_Shed_v2_Detail'
    return m.save()

def stones():
    m=Mesh('SM_Shed_FlatStones',12944)
    for x,y,z,s,key in [(-29,-15,4,(66,58,10),'7d806d'),(28,4,7,(76,55,16),'888978'),
                         (-5,40,4,(47,44,10),'747969'),(52,43,3,(31,32,8),'8a8c7a')]:
        m.ellipsoid((x,y,z),s,key,7,3,rot=(0,0,m.rng.uniform(-30,30)))
    return m.save()
