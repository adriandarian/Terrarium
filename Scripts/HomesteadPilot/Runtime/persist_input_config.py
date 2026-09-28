"""Persist exactly six pilot input mappings; plain-text config edit, no editor call.

Run with regular project Python after setup_explorer. The live editor has already
received the same bindings. This small explicit patch avoids rewriting unrelated
input defaults when SaveKeyMappings does not persist project DefaultInput.ini.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
path = ROOT / 'Config/DefaultInput.ini'
original = path.read_bytes()
text = original.decode('utf-8-sig')
newline = '\r\n' if b'\r\n' in original else '\n'
specs = [('HP_MoveForward','W',1.),('HP_MoveForward','S',-1.),
         ('HP_MoveRight','D',1.),('HP_MoveRight','A',-1.),
         ('HP_Turn','MouseX',1.),('HP_LookUp','MouseY',-1.)]
lines = []
for axis,key,scale in specs:
    existing = re.findall(r'^\+AxisMappings=\([^\r\n]*AxisName="' + re.escape(axis) + r'"[^\r\n]*Key=' + re.escape(key) + r'\)[ \t]*$', text, re.M)
    assert len(existing) <= 1, ('Duplicate mapping',axis,key)
    if existing:
        assert 'Scale=' + format(scale,'.6f') in existing[0], ('Conflicting mapping',existing)
    else:
        lines.append('+AxisMappings=(AxisName="'+axis+'",Scale='+format(scale,'.6f')+',Key='+key+')')
if lines:
    header = '[/Script/Engine.InputSettings]'
    assert text.count(header) == 1
    text = text.replace(header, header + newline + newline.join(lines), 1)
    content = text.encode('utf-8')
    if original.startswith(b'\xef\xbb\xbf'):
        content = b'\xef\xbb\xbf' + content
    path.write_bytes(content)
out = ROOT / 'Docs/HomesteadPilot/Runtime/input-config-persistence.json'
out.write_text(json.dumps({'file':str(path), 'added_lines':lines,
    'expected_mappings':specs, 'source_readback_contains_all_six':all('AxisName="'+a+'",Scale='+format(s,'.6f')+',Key='+k in text for a,k,s in specs),
    'scope':'Only six additive pilot axis mappings; no project default map or game mode changes'},indent=2),encoding='utf-8')
print('Pilot input mappings persisted; added',len(lines),'lines.')
