import json,base64,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'Scripts'))
from unreal_mcp import rpc
r=rpc('tools/call',{'name':'call_tool','arguments':{'toolset_name':'EditorToolset.EditorAppToolset','tool_name':'CaptureEditorImage','arguments':{}}})
assert not r.get('error') and not r.get('result',{}).get('isError'),r
v=json.loads(r['result']['content'][0]['text'])['returnValue'];assert v['mimeType']=='image/png'
(R/'Docs/HomesteadPilot/PIE-walking.png').write_bytes(base64.b64decode(v['data']))
print('Saved native editor PIE image')
