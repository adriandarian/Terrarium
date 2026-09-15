"""Capture the current Unreal viewport through bundled MCP, without image edits."""
import base64
import json
import sys
from pathlib import Path
from unreal_mcp import rpc

output = Path(sys.argv[1])
result = rpc('tools/call', {'name': 'call_tool', 'arguments': {
    'toolset_name': 'EditorToolset.EditorAppToolset', 'tool_name': 'CaptureViewport',
    'arguments': {'captureTransform': None, 'annotations': None, 'bShowUI': False}}})
if result.get('error') or result.get('result', {}).get('isError'):
    raise RuntimeError(result)
capture = json.loads(result['result']['content'][0]['text'])['returnValue']
output.parent.mkdir(parents=True, exist_ok=True)
output.write_bytes(base64.b64decode(capture.pop('image')['data']))
output.with_suffix('.json').write_text(json.dumps(capture, indent=2))
print(str(output.resolve()))
