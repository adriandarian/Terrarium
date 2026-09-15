"""Sequential client for this project's bundled Unreal MCP server."""
import json
import sys
import urllib.request
from pathlib import Path

URL = 'http://127.0.0.1:8000/mcp'
SESSION = Path(__file__).resolve().parents[1] / 'Saved' / 'mcp-session.txt'

def rpc(method, params, initialize=False):
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream'}
    if not initialize:
        headers['Mcp-Session-Id'] = SESSION.read_text().strip()
    body = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params}).encode()
    with urllib.request.urlopen(urllib.request.Request(URL, body, headers), timeout=120) as response:
        if initialize:
            SESSION.parent.mkdir(parents=True, exist_ok=True)
            SESSION.write_text(response.headers['Mcp-Session-Id'])
        if 'text/event-stream' in response.headers.get('Content-Type', ''):
            for line in response:
                if line.startswith(b'data:'):
                    data = json.loads(line[5:])
                    if data.get('id') == 1:
                        return data
        else:
            return json.load(response)

if __name__ == '__main__':
    action = sys.argv[1]
    if action == 'init':
        result = rpc('initialize', {'protocolVersion': '2024-11-05', 'capabilities': {}, 'clientInfo': {'name': 'codex-terrarium', 'version': '1.0'}}, True)
    elif action == 'list':
        result = rpc('tools/call', {'name': 'list_toolsets', 'arguments': {}})
    elif action == 'describe':
        result = rpc('tools/call', {'name': 'describe_toolset', 'arguments': {'toolset_name': sys.argv[2]}})
    elif action == 'call':
        args = json.loads(Path(sys.argv[4]).read_text(encoding='utf-8-sig')) if len(sys.argv) > 4 else {}
        result = rpc('tools/call', {'name': 'call_tool', 'arguments': {'toolset_name': sys.argv[2], 'tool_name': sys.argv[3], 'arguments': args}})
    if action == 'describe':
        result = json.loads(result['result']['content'][0]['text'])
        cache = SESSION.parent / ('schema-' + sys.argv[2] + '.json')
        cache.write_text(json.dumps(result, indent=2))
        for tool in result['tools']:
            print(tool['name'], tool.get('description', ''), json.dumps(tool['inputSchema']))
    else:
        print(json.dumps(result, indent=2))
