"""Run the proven actual PIE forest contact/trunk query against V5 root heights."""
import sys
from pathlib import Path
import unreal
ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
sys.path.insert(0, str(ROOT / 'Scripts/WorldExpansion/validation_v5'))
from common import legacy_source, execute_source
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(), 'Run forest acceptance in PIE; editor foliage bodies do not establish collision behavior'
source = legacy_source('validate_forest_contacts.py')
source = source.replace('SourceAssets/WorldExpansion/Terrain/manifest.json', 'SourceAssets/WorldExpansion/TerrainV5/manifest.json')
# Keep the world occlusion result instead of mistaking a foreground terrain ledge
# for a missing trunk body. Only the separate capsule identity query ignores
# terrain; root-ground queries keep their existing real-world behavior unchanged.
old_ray = "    trunk = trace([x - 80, y, visual_bottom + 100], [x + 80, y, visual_bottom + 100], False, [])"
new_ray = """    world_x = trace([x - 80, y, visual_bottom + 100], [x + 80, y, visual_bottom + 100], False, [])
    world_y = trace([x, y - 80, visual_bottom + 100], [x, y + 80, visual_bottom + 100], False, [])
    for world_hit in (world_x, world_y):
        world_hit['matched_tree_instance'] = bool(world_hit['blocking_hit'] and world_hit.get('component') == comp.get_path_name() and world_hit.get('instance_index') == instance_index)
    row['full_world_trunk_rays'] = {'x': world_x, 'y': world_y}
    terrain_only = [a for a in actors if a.get_actor_label().startswith(('WX_Terrain_', 'WX_VoxelGround_', 'WX_VoxelRock_', 'WX_VoxelHomeGround', 'WX_VoxelHomeRock')) or a.get_actor_label() == 'WX_HomeApron']
    trunk = trace([x - 80, y, visual_bottom + 100], [x + 80, y, visual_bottom + 100], False, terrain_only)
    trunk['ignored_terrain_only'] = True
    row['full_world_clear_axis_found'] = bool(world_x['matched_tree_instance'] or world_y['matched_tree_instance'])"""
assert source.count(old_ray) == 1, 'Legacy forest ray changed; review V5 adaptation'
source = source.replace(old_ray, new_ray)
source = source.replace("'limits': 'Root bounds", "'capsule_query_method': 'Full-world X and Y rays retained per sample, plus exact trunk component/instance identification with only regional terrain actors ignored. Real terrain root-contact traces are unchanged.',\n          'limits': 'Root bounds")
execute_source(source, 'validate_forest_contacts.py')
groves = ROOT / 'Docs/WorldExpansion/forest-groves-v5-integration.json'
if groves.exists():
    import json
    data = json.loads(groves.read_text())
    points = [{'location_m': [v / 100 for v in row['ground_cm']]} for row in data['instances']]
    second = source.replace("forest = source['forest_instances']", 'forest = ' + repr(points))
    second = second.replace('forest-contact-play.json', 'forest-groves-contact-play.json')
    execute_source(second, 'validate_forest_contacts.py')
