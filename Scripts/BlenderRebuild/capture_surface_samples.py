"""Capture a small representative sample of imported Unreal materials."""
import sys,json,base64
from pathlib import Path
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root/'Scripts'))
from unreal_mcp import rpc
dest=root/'Docs/BlenderRebuild/SurfaceLibrary'
for key in ['terrain_water_v9','terrain_cliff_face_v9_candidate','cottage_roof_tile_v6_candidate']:
    r=rpc('tools/call',{'name':'call_tool','arguments':{'toolset_name':'EditorToolset.EditorAppToolset','tool_name':'CaptureAssetImage','arguments':{'assetPath':'/Game/Terrarium/Blender/SurfaceLibrary/M_Source_'+key}}})
    assert not r.get('result',{}).get('isError'),r
    d=json.loads(r['result']['content'][0]['text'])['returnValue']
    image=d.get('image',d)
    if 'data' not in image:
        print(json.dumps(d)[:1500]);raise RuntimeError('No asset image')
    (dest/(key+'-unreal.png')).write_bytes(base64.b64decode(image['data']))
    print('Captured '+key)
