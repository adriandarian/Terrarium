"""Save native editor image after the passive gameplay profile, coordinator only."""
import base64,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Scripts'))
from unreal_mcp import rpc
r=rpc('tools/call',{'name':'call_tool','arguments':{'toolset_name':'EditorToolset.EditorAppToolset','tool_name':'CaptureEditorImage','arguments':{}}})
assert not r.get('error') and not r.get('result',{}).get('isError'),r
v=json.loads(r['result']['content'][0]['text'])['returnValue']
assert v['mimeType']=='image/png'
(ROOT/'Docs/HomesteadPilot/Completion/Gameplay.png').write_bytes(base64.b64decode(v['data']))
