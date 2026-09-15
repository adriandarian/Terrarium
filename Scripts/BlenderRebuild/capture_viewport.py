"""Read-only MCP viewport capture after inspect_lighting.py records camera args."""
import sys,json,base64
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Scripts'))
from unreal_mcp import rpc
argfile=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'Saved/blender-capture.json'
r=rpc('tools/call',{'name':'call_tool','arguments':{'toolset_name':'EditorToolset.EditorAppToolset','tool_name':'CaptureViewport','arguments':json.loads(argfile.read_text())}})
assert not r.get('error') and not r.get('result',{}).get('isError'),r
d=json.loads(r['result']['content'][0]['text'])['returnValue'];im=d.pop('image')
assert im['mimeType']=='image/png' and im['data']
dest=Path(sys.argv[2]) if len(sys.argv)>2 else ROOT/'Docs/BlenderRebuild/Cottage'
dest.mkdir(parents=True,exist_ok=True)
(dest/'unreal-viewport.png').write_bytes(base64.b64decode(im['data']))
(dest/'unreal-camera.json').write_text(json.dumps(d,indent=2))
print('Saved native Unreal viewport and camera evidence.')
