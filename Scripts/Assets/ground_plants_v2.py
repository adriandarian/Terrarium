"""Low fern, fine meadow grass, and cream/gold flower accents, in centimeters."""
import math
from meshkit import Mesh


def recipe(kind='fern'):
    names = {'fern': 'SM_GroundPlants_v2', 'grass': 'SM_MeadowGrass_v2',
             'flowers': 'SM_MeadowFlowers_v2'}
    m = Mesh(names[kind], 1172)
    m.refinement_pass = 7
    if kind == 'fern':
        for i in range(7):
            a = i * math.tau / 7 + .2
            length = m.rng.uniform(24, 40)
            dx, dy = math.cos(a), math.sin(a)
            m.beam((0, 0, 2), (dx*length, dy*length, 17), 1.5, 'leaf_dark')
            for step in range(1, 5):
                t = step / 5
                for side in (-1, 1):
                    reach = 12 * (1-t) + 3
                    p = (dx*length*t, dy*length*t, 2+15*t)
                    q = (p[0]+dx*4-dy*reach*side, p[1]+dy*4+dx*reach*side, p[2]+3)
                    m.beam(p, q, 4.2*(1-t)+1.2,
                           'leaf_light' if step > 2 else 'leaf', depth=1.8)
    elif kind == 'grass':
        for i in range(13):
            a = m.rng.uniform(0, math.tau)
            x, y = m.rng.uniform(-15,15), m.rng.uniform(-15,15)
            h = m.rng.uniform(16, 35)
            m.beam((x,y,0), (x+math.cos(a)*8,y+math.sin(a)*8,h),
                   m.rng.uniform(1.5,2.5), m.rng.choice(['grass','grass_light','leaf']), depth=1.2)
    else:
        for i in range(7):
            x, y = m.rng.uniform(-28,28), m.rng.uniform(-22,22)
            h = m.rng.uniform(19,34)
            m.beam((x,y,0),(x+2,y,h),1.4,'leaf_dark')
            m.ellipsoid((x-4,y,8),(12,4,3),'leaf',5,3,rot=(0,-25,i*43))
            key = 'ede0ac' if i % 3 else 'dbb942'
            for j in range(5):
                a = j * math.tau / 5
                m.ellipsoid((x+2+math.cos(a)*3.5,y+math.sin(a)*3.5,h),
                            (6,5,3),key,5,3)
            m.ellipsoid((x+2,y,h+1.5),(3.5,3.5,3),'wheat',5,3)
    return m


def build():
    return recipe().save()


def build_variants():
    return [recipe(kind).save() for kind in ('fern', 'grass', 'flowers')]
