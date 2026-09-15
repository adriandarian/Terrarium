"""Original static garden lantern post; golden panes are matte colored geometry."""
from meshkit import Mesh
def build():
    m=Mesh('SM_LanternPost',292)
    m.box((0,0,13),(42,40,26),'77795c',5)
    m.box((0,0,101),(13,13,178),'45452d',2)
    m.box((0,0,192),(32,31,39),'c7a74d',3)
    for x in [-19,19]:
        for y in [-18,18]:m.beam((x,y,169),(x*.7,y*.7,217),4,'414330')
    m.box((0,0,167),(47,45,7),'555640',2)
    m.ellipsoid((0,0,221),(55,53,30),'4c5039',6,3)
    m.ellipsoid((0,0,240),(12,12,15),'8d8a64',6,3)
    return m.save()
