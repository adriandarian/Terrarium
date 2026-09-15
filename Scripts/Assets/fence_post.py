"""Separate reusable timber post, irregular cap, and stone foot."""
from meshkit import Mesh
def build():
    m=Mesh('SM_FencePost',31)
    m.box((0,0,9),(29,28,18),'stone',4)
    m.box((0,0,65),(18,20,123),'wood',3,rot=(0,1,1))
    m.box((1,0,130),(25,26,15),'wood_light',4)
    m.box((-2,-11,89),(11,4,28),'wood_light',1)
    return m.save()
if __name__=='__main__':build()
