"""Reserve otherwise unused atlas space for crisp face and belly pigments."""
from collections import Counter
import json
import bpy


def map_surfaces(asset):
    bpy.context.view_layer.update()
    vertices=[ob.matrix_world@v.co for ob in asset.parts for v in ob.data.vertices]
    lo=[min(v[i] for v in vertices) for i in range(3)]
    hi=[max(v[i] for v in vertices) for i in range(3)]
    rows=[];selected={4:[],5:[]}
    for ob in asset.parts:
        uv=ob.data.uv_layers.active
        attribute=ob.data.attributes.get('pigment') or ob.data.attributes.new('pigment','INT','FACE')
        for face in ob.data.polygons:
            counts=Counter(min(15,max(0,int(uv.data[j].uv.y*8)*8+int(uv.data[j].uv.x*8))) for j in face.loop_indices)
            pigment=counts.most_common(1)[0][0];attribute.data[face.index].value=pigment
            axis=max(range(3),key=lambda i:abs(face.normal[i]))
            row=(ob,face.index,pigment,axis);rows.append(row)
            if pigment in selected and axis==1:
                selected[pigment].extend(ob.matrix_world@ob.data.vertices[ob.data.loops[j].vertex_index].co for j in face.loop_indices)
    layouts={}
    for pigment,xstart in [(5,16),(4,528)]:
        points=selected[pigment];assert points
        layouts[pigment]={'pixel_rect':[xstart,288,xstart+480,1008],
            'uv_min':[(xstart+4)/1024,292/1024], 'uv_max':[(xstart+476)/1024,1004/1024],
            'world_xz_bounds_m':[min(p.x for p in points),max(p.x for p in points),min(p.z for p in points),max(p.z for p in points)]}
    counts={4:0,5:0}
    for ob,index,pigment,axis in rows:
        face=ob.data.polygons[index];uv=ob.data.uv_layers.active
        axes=[i for i in range(3) if i!=axis]
        for loop in face.loop_indices:
            v=ob.matrix_world@ob.data.vertices[ob.data.loops[loop].vertex_index].co
            if pigment in layouts and axis==1:
                m=layouts[pigment];xmin,xmax,zmin,zmax=m['world_xz_bounds_m']
                uv.data[loop].uv=tuple(m['uv_min'][j]+(m['uv_max'][j]-m['uv_min'][j])*t for j,t in enumerate([(v.x-xmin)/(xmax-xmin),(v.z-zmin)/(zmax-zmin)]))
            else:
                uv.data[loop].uv=tuple((pigment%8 if j==0 else pigment//8)/8+.006+.113*(v[a]-lo[a])/(hi[a]-lo[a]) for j,a in enumerate(axes))
        if pigment in layouts and axis==1:counts[pigment]+=1
        ob['surface_uv_mapping']='Planar pigment cells with dedicated face and belly regions'
    for pigment,m in layouts.items():m['boundary_faces']=counts[pigment]
    (asset.review/'face-atlas-layout.json').write_text(json.dumps({'atlas_size':[1024,1024],'regions':layouts,'method':'Two 480 by 720 pixel regions with four-pixel gutters use the face and belly local X/Z bounds. Other surfaces retain their original pigment cells.'},indent=2))
    return lo,hi,layouts
