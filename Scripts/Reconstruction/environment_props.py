"""Reusable, unsaved environmental props extracted from the compound recipes.

Each wrapper builds one prop at its local origin, reflects source X exactly once,
then grounds its geometric minimum at Z=0. Shared recipes are left unchanged.
"""
from meshkit import Mesh
import architecture
import compound

SPECS={
    'house':{'name':'SM_Env_Cottage','recipe':'compound.house','front_axis':[0,-1,0],
             'scene_yaw_degrees_for_camera_yaw135':90,
             'features':'Narrow door elevation, deeper two-window side, open chimney, side dormer and timber entrance steps.'},
    'shed':{'name':'SM_Env_BlueShed','recipe':'compound.shed','front_axis':[0,-1,0],
            'scene_yaw_degrees_for_camera_yaw135':0,
            'features':'Low compact timber shed, teal stepped roof, framed front door and narrow footing.'},
    'garden':{'name':'SM_Env_VegetableBed','recipe':'compound.garden','front_axis':[0,-1,0],
              'scene_yaw_degrees_for_camera_yaw135':0,
              'features':'Five by four leafy vegetable planting grid within low timber edging.'},
    'tower':{'name':'SM_Env_Tower','recipe':'compound.tower','front_axis':[0,-1,0],
             'scene_yaw_degrees_for_camera_yaw135':0,
             'features':'Stone-footed timber beacon with amber chamber and irregular grey stone crest.'},
    'small_lantern':{'name':'SM_Env_Lantern','recipe':'compound.small_lantern','front_axis':[0,-1,0],
                     'scene_yaw_degrees_for_camera_yaw135':0,
                     'features':'Slim freestanding lantern post with compact amber cage and stone foot.'},
    'flower_row':{'name':'SM_Env_FlowerBorder','recipe':'compound.flower_row','front_axis':[0,-1,0],
                  'scene_yaw_degrees_for_camera_yaw135':0,
                  'features':'Low orange flower border with dense green base and tall sunflower at one end.'},
}

_RECIPES={'house':compound.house,'shed':compound.shed,'garden':compound.garden,
          'tower':compound.tower,'small_lantern':compound.small_lantern,
          'flower_row':compound.flower_row}


def _build(key):
    spec=SPECS[key]
    m=Mesh(spec['name'],2041+list(SPECS).index(key))
    m.refinement_pass=1
    _RECIPES[key](m)
    architecture.reflect_source_handedness(m)
    low=min(v[2] for v in m.vertices)
    if low:
        m.vertices=[(x,y,z-low) for x,y,z in m.vertices]
        for part in m.parts:
            x,y,z=part['center'];part['center']=(x,y,z-low)
    bounds={'min':[min(v[i] for v in m.vertices) for i in range(3)],
            'max':[max(v[i] for v in m.vertices) for i in range(3)]}
    spec['bounds_cm']=bounds
    spec['dimensions_cm']=[round(bounds['max'][i]-bounds['min'][i],4) for i in range(3)]
    spec['triangles']=len(m.triangles)
    spec['source_x_reflected']=True
    spec['ground_offset_applied_cm']=-low
    m.source_reference='homestead_compound.png; environment image-1.png'
    return m


def house():return _build('house')
def shed():return _build('shed')
def garden():return _build('garden')
def tower():return _build('tower')
def small_lantern():return _build('small_lantern')
def flower_row():return _build('flower_row')


BUILDERS={'house':house,'shed':shed,'garden':garden,'tower':tower,
          'small_lantern':small_lantern,'flower_row':flower_row}
