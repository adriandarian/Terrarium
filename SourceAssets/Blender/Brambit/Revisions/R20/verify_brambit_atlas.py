"""Verify saved UV allocation and local surface texel density."""
import bpy,json,hashlib
from pathlib import Path
r=Path('C:/Users/hello/Projects/Terrarium');s=bpy.context.scene
assert Path(s.get('terrarium_project',''))==r and s['asset_name']=='Brambit'
out=r/'Docs/BlenderRebuild/Brambit';source=r/'SourceAssets/Blender/Brambit/Brambit.blend'
layout=json.loads((out/'face-atlas-layout.json').read_text())
mesh=json.loads((out/'mesh-validation.json').read_text())
assert layout['atlas_size']==[1024,1024]
counts={4:0,5:0};loops=0;maximum_error=0
for ob in [o for o in s.objects if o.get('part')]:
    data=ob.data;attribute=data.attributes['pigment'];uv=data.uv_layers.active
    for face in data.polygons:
        pigment=attribute.data[face.index].value
        axis=max(range(3),key=lambda i:abs(face.normal[i]))
        special=pigment in counts and axis==1
        if special:
            m=layout['regions'][str(pigment)];xmin,xmax,zmin,zmax=m['world_xz_bounds_m'];counts[pigment]+=1
        for i in face.loop_indices:
            actual=uv.data[i].uv
            if special:
                v=ob.matrix_world@data.vertices[data.loops[i].vertex_index].co
                expected=[m['uv_min'][j]+(m['uv_max'][j]-m['uv_min'][j])*t for j,t in enumerate([(v.x-xmin)/(xmax-xmin),(v.z-zmin)/(zmax-zmin)])]
                error=max(abs(actual[j]-expected[j]) for j in range(2));maximum_error=max(maximum_error,error)
                assert error<1e-6
                loops+=1
            else:
                # The remaining surfaces must stay in the original pigment
                # rows, clear of both new rectangular allocations.
                assert 0<actual.x<1 and 0<actual.y<.25
assert all(counts[p]==layout['regions'][str(p)]['boundary_faces']>0 for p in counts)
rows=[]
for p,count in counts.items():
    m=layout['regions'][str(p)];xmin,xmax,zmin,zmax=m['world_xz_bounds_m']
    dimensions=[xmax-xmin,zmax-zmin]
    density=[1024*(m['uv_max'][i]-m['uv_min'][i])/dimensions[i] for i in range(2)]
    old=[1024*.113/(mesh['bounds_m']['max'][axis]-mesh['bounds_m']['min'][axis]) for axis in [0,2]]
    rows.append({'pigment':p,'boundary_faces':count,'mapped_pixels':[472,712],'texels_per_m_xz':density,'previous_texels_per_m_xz':old,'density_multiplier_xz':[density[i]/old[i] for i in range(2)]})
result={'source_blend_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'layout_sha256':hashlib.sha256((out/'face-atlas-layout.json').read_bytes()).hexdigest(),'uv_loops_checked':loops,'maximum_uv_error':maximum_error,'regions':rows,'method':'Read the saved polygon pigment attribute and verify each face/belly UV against its actual world-space surface position. Check every remaining UV remains in the original atlas rows.','limits':'UV allocation and geometric texel density. Appearance is evaluated separately from studio and Unreal renders; no overall fidelity claim.'}
(out/'face-atlas-verification.json').write_text(json.dumps(result,indent=2))
