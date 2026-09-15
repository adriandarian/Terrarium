"""Irregular flush moss patches: color detail without dense raised pebble shadows."""
from meshkit import Mesh

def build():
    m=Mesh('SM_MeadowTile_v4',482);m.refinement_pass=4;m.revises='SM_MeadowTile_v3'
    m.box((0,0,-160),(203,203,320),'555b3e',2)
    m.box((0,0,-2),(206,206,15),'697435',3,variation=.02)
    for i in range(43):
        x=m.rng.uniform(-93,93);y=m.rng.uniform(-93,93)
        m.box((x,y,6+i*.006),(m.rng.uniform(22,63),m.rng.uniform(21,55),1),m.rng.choice(['7a823e','858947','657334','71803a','8b9047','5e6d32','74803b']),1,rot=(0,0,m.rng.uniform(-16,16)),variation=.02)
    for x,y in [(-63,19),(67,-56)]:
        for d in [-3,4]:m.box((x+d,y,11),(5,4,m.rng.uniform(10,15)),'778341',1,rot=(0,0,13))
    result=m.save()
    import unreal,json
    from pathlib import Path
    sm=unreal.load_asset('/Game/Terrarium/Meshes/SM_MeadowTile_v4')
    mat=unreal.load_asset('/Game/Terrarium/Materials/M_WeatheredDetails')
    assert sm and mat
    sm.set_material(0,mat);assert unreal.EditorAssetLibrary.save_loaded_asset(sm)
    p=Path(unreal.Paths.project_dir(),'Docs/Phase1/Validation/SM_MeadowTile_v4.json')
    report=json.loads(p.read_text());report['surface_material']=mat.get_path_name()
    p.write_text(json.dumps(report,indent=2))
    return result
