"""Crop-only placement module, sharing the complete reference bed's stalk recipe."""
import sys, importlib
sys.path.insert(0, 'C:/Users/hello/Projects/Terrarium/Scripts/BlenderRebuild')
import wheat_field
importlib.reload(wheat_field)
result = wheat_field.build('WheatPatch', 8, 7, .17, False)
