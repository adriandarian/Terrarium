"""Losslessly pack the supplied stone and grass images into one material atlas."""
from PIL import Image
from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parents[2]
stone=Image.open(root/'SourceAssets/Voxel/terrain_cliff_face_v7.png').convert('RGB')
grass=Image.open(root/'SourceAssets/Voxel/terrain_grass_top_v9.png').convert('RGB')
assert stone.size==grass.size==(1254,1254)
atlas=Image.new('RGB',(2508,1254));atlas.paste(stone,(0,0));atlas.paste(grass,(1254,0))
folder=root/'SourceAssets/Blender/CliffColumn';folder.mkdir(exist_ok=True)
path=folder/'CliffColumn_SourceAtlas.png';atlas.save(path)
check=Image.open(path)
assert check.crop((0,0,1254,1254)).tobytes()==stone.tobytes()
assert check.crop((1254,0,2508,1254)).tobytes()==grass.tobytes()
review=root/'Docs/BlenderRebuild/CliffColumn';review.mkdir(exist_ok=True)
(review/'atlas-verification.json').write_text(json.dumps({'source_images':['terrain_cliff_face_v7.png','terrain_grass_top_v9.png'],'dimensions_px':[2508,1254],'both_rgb_regions_pixel_identical':True,'atlas_sha256':hashlib.sha256(path.read_bytes()).hexdigest()},indent=2))
print('Packed and verified both source RGB regions without resizing or color changes.')
