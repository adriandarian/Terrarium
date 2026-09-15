"""Render each saved static mesh through Unreal's asset thumbnail renderer."""
import base64
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'Scripts'))
from unreal_mcp import rpc
for group in ['characters', 'structures']:
    for record in json.loads((ROOT / 'Docs/AssetMigration' / (group+'-built.json')).read_text()):
        result = rpc('tools/call', {'name':'call_tool','arguments':{'toolset_name':'EditorToolset.EditorAppToolset','tool_name':'CaptureAssetImage','arguments':{'assetPath':record['asset']}}})
        assert not result.get('error') and not result.get('result',{}).get('isError'), result
        data = json.loads(result['result']['content'][0]['text'])['returnValue']
        path = ROOT / 'Docs/AssetMigration/Models' / (record['name']+'.png')
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(base64.b64decode(data['data']))
        print(path,flush=True)
