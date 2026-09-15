"""Stone stair flight: 8 treads, descending toward negative Y."""
from meshkit import Mesh
def build():
    m=Mesh('SM_StoneStairs',44)
    for i in range(8):
        y=-147+i*42;h=30*(i+1)
        m.box((0,y,h/2),(200,43,h),'stone',5)
        for x in [-49,49]:m.box((x,y,h+3),(98,45,12),m.rng.choice(['stone_light','stone']),4)
        for x in [-111,111]:
            m.box((x,y,h/2+10),(24,41,h+20),'stone_dark',4)
            if i%3==0:m.box((x,y,h+20),(28,42,10),'moss',3)
    return m.save()
if __name__=='__main__':build()
