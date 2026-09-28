"""One focused correction: stair clearance and measured silhouette widths.

Run only in the saved ConceptScaleBlockout. No camera or anchor movement.
Creates dedicated replacement meshes; old mesh assets remain recoverable.
"""
import ast
import json
import math
from pathlib import Path
import unreal

ROOT=Path(unreal.Paths.project_dir()).resolve()
assert Path(unreal.Paths.get_project_file_path()).stem=='Terrarium'
LEVEL='/Game/Terrarium/Calibration/Maps/ConceptScaleBlockout'
ASSETS='/Game/Terrarium/Calibration/ScaleBlockoutStairNotch'
LEVELS=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ACTORS=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert LEVEL+'.' in str(LEVELS.get_current_level()), 'Open the new calibration map first'
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages(), 'Preserve unsaved changes first'
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages(), 'Preserve unsaved assets first'
assert not unreal.EditorAssetLibrary.does_directory_exist(ASSETS), 'One correction already attempted; inspect before repeating'
DATA=json.loads((ROOT/'Docs/ScaleCalibration/targets.json').read_text())
W,H=DATA['image_size_px'];S=5.5;K=math.sqrt(.5);RECORDS=[]
scene={a.get_actor_label():a for a in ACTORS.get_all_level_actors()}
original=[scene['Scale_Terrace_main'],scene['Scale_Turf_main']]


def material(key):
    result=unreal.load_asset('/Game/Terrarium/Calibration/ScaleBlockout/Materials/M_Scale_'+key)
    assert result,key
    return result


# Reuse only pure helper function definitions, never the build script's body.
source=ROOT/'Scripts/ScaleCalibration/build_blockout.py'
tree=ast.parse(source.read_text(encoding='utf-8'))
names={'world','pixel','cross2','triangulate','spawn','mesh','prism','raised_prism'}
for node in tree.body:
    if isinstance(node,ast.FunctionDef) and node.name in names:
        exec(compile(ast.Module(body=[node],type_ignores=[]),str(source),'exec'),globals())


def area(poly):
    return sum(p[0]*q[1]-q[0]*p[1] for p,q in zip(poly,poly[1:]+poly[:1]))/2


def clip(poly,a,b,keep_inside):
    """Clip one convex polygon against an oriented corridor half-plane."""
    result=[]
    for p,q in zip(poly,poly[1:]+poly[:1]):
        dp=cross2(a,b,p);dq=cross2(a,b,q)
        inp=dp>=-1e-7 if keep_inside else dp<=1e-7
        inq=dq>=-1e-7 if keep_inside else dq<=1e-7
        if inp:result.append(p)
        if inp!=inq:
            t=dp/(dp-dq)
            result.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
    clean=[]
    for p in result:
        if not clean or math.dist(p,clean[-1])>1e-5:clean.append(p)
    if len(clean)>1 and math.dist(clean[0],clean[-1])<1e-5:clean.pop()
    return clean if len(clean)>=3 and abs(area(clean))>1e-5 else []


def difference(triangle,corridor):
    """Disjoint convex pieces of triangle minus convex stair corridor."""
    pending=triangle;pieces=[]
    for a,b in zip(corridor,corridor[1:]+corridor[:1]):
        if not pending:break
        outside=clip(pending,a,b,False)
        if outside:pieces.append(outside)
        pending=clip(pending,a,b,True)
    return pieces


stair=next(o for o in DATA['objects'] if o['id']=='stairs')
points=[world(*p,560)[:2] for p in stair['top_edge_px']]
points += [world(*p,280)[:2] for p in reversed(stair['bottom_edge_px'])]
center=tuple(sum(p[k] for p in points)/4 for k in range(2))
# 12% lateral clearance avoids z-fighting against the stair cheek surfaces.
corridor=[tuple(center[k]+(p[k]-center[k])*1.12 for k in range(2)) for p in points]
if area(corridor)<0:corridor.reverse()
main=next(t for t in DATA['terraces'] if t['id']=='main')
poly=[world(x,y,560)[:2] for x,y in main['polygon_px']]
parts=[]
for t in triangulate(poly):parts.extend(difference([poly[i] for i in t],corridor))
assert parts and sum(abs(area(p)) for p in parts)<abs(area(poly)), 'Corridor must remove terrace overlap'


def combined_prisms(label,top,bottom,key):
    verts=[];faces=[]
    for part in parts:
        if area(part)<0:part=list(reversed(part))
        offset=len(verts);n=len(part)
        verts.extend((x,y,bottom) for x,y in part)
        verts.extend((x,y,top) for x,y in part)
        tris=triangulate(part)
        faces.extend(tuple(offset+i for i in reversed(t)) for t in tris)
        faces.extend(tuple(offset+n+i for i in t) for t in tris)
        faces.extend((offset+i,offset+(i+1)%n,offset+(i+1)%n+n,offset+i+n) for i in range(n))
    return mesh(label,verts,faces,key)


combined_prisms('Terrace_main_notched',558,-1,'stone')
combined_prisms('Turf_main_notched',560,557,'grass')

# Re-evaluate only the existing cottage geometry recipe into plain arrays.
# This does not execute the build script's editor initialization or scene body.
captured=[]
real_mesh=mesh
def capture_mesh(label,verts,faces,key):captured.append((label,verts,faces,key))
OBJECTS={o['id']:o for o in DATA['objects']}
ELEVATIONS=DATA['scale_convention']['terrace_heights']
building_loops=[n for n in tree.body if isinstance(n,ast.For) and isinstance(n.iter,ast.Tuple)
    and ast.literal_eval(n.iter)==('cottage','shed')]
assert len(building_loops)==1, 'Original building recipe changed; inspect before patching'
mesh=capture_mesh
try:
    exec(compile(ast.Module(body=building_loops,type_ignores=[]),str(source),'exec'),globals())
    px,py=OBJECTS['person']['anchor_px'];base=560
    footprint=[(px-5,py-2),(px,py+1),(px+5,py-2),(px,py-5)]
    raised_prism('Person_body',footprint,base,145,'person')
    raised_prism('Person_head',[(x,y-145*K/S) for x,y in footprint],base+145,35,'wall')
finally:
    mesh=real_mesh

size_changes=[]
for prefix,anchor,target_width in [('cottage',251,117),('Person',177,18)]:
    group=[r for r in captured if r[0].startswith(prefix)]
    xs=[pixel(v)[0] for label,vs,faces,key in group for v in vs]
    before_width=max(xs)-min(xs);factor=target_width/before_width
    before_points=[pixel(v) for label,vs,faces,key in group for v in vs]
    after_points=[]
    for label,vs,faces,key in group:
        transformed=[]
        for v in vs:
            x,y=pixel(v)
            transformed.append(world(anchor+(x-anchor)*factor,y,v[2]))
        after_points.extend(pixel(v) for v in transformed)
        mesh(label+'_measured',transformed,faces,key)
        original.append(scene['Scale_'+label])
    size_changes.append({'object':prefix,'anchor_x_px':anchor,'screen_horizontal_factor':factor,
        'before_width_px':before_width,'after_width_px':target_width,'height_and_contact_preserved':True,
        'before_bounds_px':[min(p[0] for p in before_points),min(p[1] for p in before_points),max(p[0] for p in before_points),max(p[1] for p in before_points)],
        'after_bounds_px':[min(p[0] for p in after_points),min(p[1] for p in after_points),max(p[0] for p in after_points),max(p[1] for p in after_points)]})

# Replace only listed calibration actors after all replacement meshes exist.
for actor in original:assert ACTORS.destroy_actor(actor)
assert LEVELS.save_current_level(), 'No correction receipt: save failed'
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
receipt={'level':LEVEL,'saved':True,'correction_pass':1,'scope':'main terrace stair corridor plus cottage and person measured horizontal widths',
    'camera_unchanged':True,'original_assets_retained':True,'convex_parts':len(parts),
    'removed_ground_area_world_units_squared':abs(area(poly))-sum(abs(area(p)) for p in parts),
    'corridor_projected_at_main_height':[pixel((x,y,560)) for x,y in corridor],
    'size_changes':size_changes,'generated_meshes':RECORDS,'visual_review':'pending native recapture'}
(ROOT/'Docs/ScaleCalibration/stair-notch-receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
unreal.log('TERRARIUM_SCALE_STAIR_NOTCH_SAVED')
