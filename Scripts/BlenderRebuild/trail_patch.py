import sys,importlib
sys.path.insert(0,'C:/Users/hello/Projects/Terrarium/Scripts/BlenderRebuild')
import trail_terrain
importlib.reload(trail_terrain)
result=trail_terrain.build('TrailPatch',True)
