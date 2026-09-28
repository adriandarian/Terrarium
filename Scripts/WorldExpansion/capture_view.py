"""Save the actual Unreal MCP viewport, after staging and allowing rendering."""
import json,sys,base64
from pathlib import Path
R=Path(__file__).resolve().parents[2];D=R/'Docs/WorldExpansion'
sys.path.insert(0,str(R/'Scripts'))
from unreal_mcp import rpc
name=json.loads((D/'view-request.json').read_text())['name']
args=json.loads((D/'capture-request.json').read_text())
args['annotations']={'gridSpacing':0,'gridExtent':0,'gridHeight':0,'maxLabelDistance':0,'classFilter':{'refPath':'/Script/Engine.Actor'},'maxLabels':0}
r=rpc('tools/call',{'name':'call_tool','arguments':{'toolset_name':'EditorToolset.EditorAppToolset','tool_name':'CaptureViewport','arguments':args}})
assert not r.get('error') and not r.get('result',{}).get('isError'),r
v=json.loads(r['result']['content'][0]['text'])['returnValue']
im=v.pop('image');assert im['mimeType']=='image/png'
out=D/'Captures';out.mkdir(parents=True,exist_ok=True)
(out/(name+'.png')).write_bytes(base64.b64decode(im['data']))
(out/(name+'.json')).write_text(json.dumps(v,indent=2))
print(name)
