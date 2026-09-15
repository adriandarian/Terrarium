"""Run an editor Python file through the verified Terrarium MCP console."""
import json
import re
import sys
import time
from pathlib import Path
from unreal_mcp import rpc

def call(name, args):
    r = rpc('tools/call', {'name':'call_tool','arguments': {
        'toolset_name':'SlateInspectorToolset.SlateInspectorToolset',
        'tool_name':name,'arguments':args}})
    if r.get('error') or r.get('result',{}).get('isError'):
        raise RuntimeError(r)
    return json.loads(r['result']['content'][0]['text'])['returnValue']

assert 'Terrarium - Unreal Editor' in call('Windows', {})
call('Observe', {'ref':'','maxDepth':60})
time.sleep(0.25)
snapshot = call('Snapshot', {'ref':'','maxDepth':60})
inputs = re.findall(r'^\s*textbox (?:\[focused\] )?\[pos=[^\n]+\[ref=(\w+)\]', snapshot, re.M)
assert inputs, 'No console input found'
script = str(Path(sys.argv[1]).resolve()).replace('\\','/')
print(call('Type', {'ref':inputs[-1],'text':'py "'+script+'"','submit':True}))
