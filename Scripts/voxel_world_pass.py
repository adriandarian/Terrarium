"""Native, reversible voxel art-direction pass; execute in Terrarium editor."""
import unreal, sys, json, math
from pathlib import Path
from collections import Counter

assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root = Path(unreal.Paths.project_dir())
out = root / 'Docs/VoxelPass'
out.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(root / 'Scripts/Assets'))
from meshkit import Mesh
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert '/HomesteadFidelity.' in str(levels.get_current_level())
assert levels.save_current_level()
backup = '/Game/Terrarium/Maps/HomesteadBeforeVoxelPass'
if not unreal.EditorAssetLibrary.does_asset_exist(backup):
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    assert unreal.EditorLoadingAndSavingUtils.save_map(world, backup)
    world = None
    assert levels.load_level('/Game/Terrarium/Maps/HomesteadFidelity')

class VoxelMesh(Mesh):
    def box(self, pos, size, key, bevel=0, rot=(0,0,0), variation=.025):
        x,y,z = (s/2 for s in size)
        vertices = [(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),
                    (-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
        self.solid(vertices, [[0,1,2,3],[4,5,6,7],[0,1,5,4],
                             [1,2,6,5],[2,3,7,6],[3,0,4,7]], key, rot, pos, variation)

def save(m):
    path = '/Game/Terrarium/Meshes/' + m.name
    return unreal.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else m.save()

replacements = {}
for index, variant in enumerate('ABC'):
    m = VoxelMesh('SM_VoxelCliff_' + variant, 914 + index)
    m.box((0,0,151), (84,84,302), '53593e')
    # Square stone faces, small seams, no chamfer highlight or horizontal slabs.
    for row in range(5):
        for ix in range(2):
            for iy in range(2):
                tint = m.rng.choice(['777553','85805b','696d4c','777954','656c4a'])
                m.box(((ix-.5)*49,(iy-.5)*49,row*61+30.5),
                      (m.rng.choice([45,49,55]),m.rng.choice([45,49,55]),59.5),tint)
    for ix in range(3):
        for iy in range(3):
            top = 323.5 if (ix,iy)==(1,1) else m.rng.choice([319.5,321.5,323.5])
            m.box(((ix-1)*33,(iy-1)*33,top-10),(33,33,20),
                  m.rng.choice(['738238','829040','667730','8a9446']))
    for side in range(4):
        p = [m.rng.choice([-33,0,33]), m.rng.choice([-33,0,33]), 298]
        p[side%2] = (-1 if side<2 else 1)*47
        m.box(tuple(p),(16,16,m.rng.choice([25,42,58])),'65762f')
    replacements['SM_CliffColumn_v6'+variant] = save(m)

for tree in (True, False):
    m = VoxelMesh('SM_VoxelTree' if tree else 'SM_VoxelBush', 917 if tree else 918)
    if tree:
        for z in range(16,337,32):
            m.box((0,0,z),(20 if z<160 else 12,20 if z<160 else 12,32),'584328')
        centers=[(-48,16,164),(48,-32,196),(-16,48,228),(-48,-32,260),
                 (48,16,292),(-16,32,324),(0,-16,356)]
        cell=24
    else:
        centers=[(-24,0,40),(24,16,56),(0,-24,72),(0,24,88)]
        cell=20
    occupied=set()
    for cx,cy,cz in centers:
        m.beam((0,0,max(4,cz-50)),(cx,cy,cz),8,'584529')
        for ix in (-1,0,1):
            for iy in (-1,0,1):
                for iz in (0,1):
                    if (abs(ix)+abs(iy)+iz==3) or (ix and iy and m.rng.random()<.45): continue
                    p=tuple(round(v/cell)*cell for v in (cx+ix*cell,cy+iy*cell,cz+iz*cell))
                    if p in occupied:continue
                    occupied.add(p)
                    m.box(p,(cell,cell,cell),m.rng.choice(['405821','526a25','6a7e2e','7e8e37','8d983f']))
    replacements['SM_Tree_v3' if tree else 'SM_Bush_v2'] = save(m)

lib=unreal.MaterialEditingLibrary
def material(name, ground=False):
    path='/Game/Terrarium/Materials/'+name
    mat=unreal.load_asset(path)
    if mat:return mat
    mat=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,'/Game/Terrarium/Materials',unreal.Material,unreal.MaterialFactoryNew())
    mat.set_editor_property('used_with_instanced_static_meshes',True)
    vertex=lib.create_material_expression(mat,unreal.MaterialExpressionVertexColor,-600,-100)
    pos=lib.create_material_expression(mat,unreal.MaterialExpressionWorldPosition,-600,100)
    custom=lib.create_material_expression(mat,unreal.MaterialExpressionCustom,-250,0)
    custom.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    inputs=[]
    for name in ('World','Pigment'):
        pin=unreal.CustomInput();pin.set_editor_property('input_name',name);inputs.append(pin)
    custom.set_editor_property('inputs',inputs)
    if ground:
        code='''
float2 id = floor(World.xy / 24.0);
float h = frac(sin(dot(id,float2(127.1,311.7)))*43758.5453);
float broad = sin(id.x*.19+sin(id.y*.13))*sin(id.y*.17-id.x*.09)*.5+.5;
float3 earth = float3(.139,.143,.044);
float3 moss = float3(.178,.210,.042);
float3 col = lerp(earth,moss,step(.30,broad));
return col * lerp(.78,1.20,floor(h*5.0)/4.0);
'''
    else:
        code='''
float3 id = floor(World / 18.0);
float h = frac(sin(dot(id,float3(127.1,311.7,74.7)))*43758.5453);
return Pigment * lerp(.93,1.05, floor(h*3.0)/2.0);
'''
    custom.set_editor_property('code',code)
    assert lib.connect_material_expressions(pos,'',custom,'World')
    assert lib.connect_material_expressions(vertex,'',custom,'Pigment')
    assert lib.connect_material_property(custom,'',unreal.MaterialProperty.MP_BASE_COLOR)
    for prop,value in [(unreal.MaterialProperty.MP_ROUGHNESS,.96),(unreal.MaterialProperty.MP_SPECULAR,.06)]:
        c=lib.create_material_expression(mat,unreal.MaterialExpressionConstant,-250,250)
        c.set_editor_property('r',value);lib.connect_material_property(c,'',prop)
    lib.recompile_material(mat);unreal.EditorAssetLibrary.save_loaded_asset(mat)
    return mat

ground=material('M_VoxelGround',True)
surface=material('M_VoxelSurface')
report={'backup':backup,'replacements':{},'materials':{},'project':unreal.Paths.get_project_file_path()}
swaps=[]
for a in actors.get_all_level_actors():
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        mesh=c.static_mesh
        if not mesh:continue
        name=mesh.get_name()
        count=c.get_instance_count() if isinstance(c,unreal.InstancedStaticMeshComponent) else 1
        if not count:continue
        if name in replacements:
            assert isinstance(c,unreal.FoliageInstancedStaticMeshComponent)
            swaps.append((name,[c.get_instance_transform(i,world_space=True) for i in range(count)]))
            report['replacements'][name]={'new':replacements[name].get_name(),'instances':count}
        if name.startswith('SM_MeadowTile'):
            c.set_material(0,ground)
        elif name in replacements or name.startswith('SM_PathTile'):
            c.set_material(0,surface)
        else:continue
        report['materials'][c.get_path_name()]=c.get_material(0).get_path_name()
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
for name,transforms in swaps:
    # Foliage types own meshes on reload; component-only swaps are transient.
    old=unreal.load_asset('/Game/Terrarium/Foliage/FT_'+name[3:])
    assert old
    newname='FT_'+replacements[name].get_name()[3:]
    ft=unreal.load_asset('/Game/Terrarium/Foliage/'+newname)
    if not ft:
        ft=unreal.AssetToolsHelpers.get_asset_tools().create_asset(newname,'/Game/Terrarium/Foliage',unreal.FoliageType_InstancedStaticMesh,unreal.FoliageType_InstancedStaticMeshFactory())
    ft.set_editor_property('mesh',replacements[name])
    ft.set_editor_property('override_materials',[surface])
    assert unreal.EditorAssetLibrary.save_loaded_asset(ft)
    unreal.InstancedFoliageActor.remove_all_instances(world,old)
    unreal.InstancedFoliageActor.add_instances(world,ft,transforms)
world=None
for mat in (ground,surface):
    mat.set_editor_property('used_with_instanced_static_meshes',True)
    assert unreal.EditorAssetLibrary.save_loaded_asset(mat)
assert levels.save_current_level()
(out/'applied.json').write_text(json.dumps(report,indent=2))
unreal.log('VOXEL_WORLD_PASS_SAVED')
