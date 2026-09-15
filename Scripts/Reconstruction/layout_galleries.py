"""Put low assets in front, then frame actual bounds including all labels."""
import json,math,sys
from pathlib import Path
import unreal
root=Path(unreal.Paths.project_dir());sys.path.insert(0,str(root/'Scripts/Reconstruction'));import build_galleries as g
assert g.current_is(g.REVIEW);assert g.LEVELS.save_current_level()
for category,config in g.GROUPS.items():
    path=g.PKG+'/Maps/'+category;assert g.LEVELS.load_level(path)
    scene={a.get_actor_label():a for a in g.ACTORS.get_all_level_actors()}
    file=g.OUT/(category+'.json');report=json.loads(file.read_text());models=report['models']
    if category in ['Architecture','Environment']:models.sort(key=lambda r:r['world_bounds_cm']['max'][2])
    y_cursor=0;columns=config['columns'];gap=config['gap']
    for start in range(0,len(models),columns):
        line=models[start:start+columns];sizes=[]
        for r in line:
            b=g.actor_bounds(scene[r['label']]);sizes.append([b['max'][i]-b['min'][i] for i in range(3)])
        width=sum(s[0] for s in sizes)+gap*(len(line)-1);depth=max(s[1] for s in sizes);x=-width/2
        for r,size in zip(line,sizes):
            a=scene[r['label']];b=g.actor_bounds(a);p=a.get_actor_location()
            p.x+=x+size[0]/2-(b['min'][0]+b['max'][0])/2;p.y+=y_cursor+depth/2-(b['min'][1]+b['max'][1])/2;p.z-=b['min'][2]
            a.set_actor_location(p,False,False);b=g.actor_bounds(a)
            lp=unreal.Vector(x+size[0]/2,b['min'][1]-32,.3);scene[r['text_actor']].set_actor_location(lp,False,False)
            r.update({'world_bounds_cm':b,'location_cm':g.vector_list(p),'label_location_cm':g.vector_list(lp)})
            x+=size[0]+gap
        y_cursor+=depth+gap+35
    corners=[]
    for r in models:
        b=r['world_bounds_cm']
        for x in (b['min'][0]-25,b['max'][0]+25):
            for y in (b['min'][1]-55,b['max'][1]+20):
                for z in (0,b['max'][2]):corners.append((x,y,z))
    center=tuple((min(p[i] for p in corners)+max(p[i] for p in corners))/2 for i in range(3))
    pitch,yaw=-37,100
    p,y=math.radians(pitch),math.radians(yaw)
    forward=(math.cos(p)*math.cos(y),math.cos(p)*math.sin(y),math.sin(p));right=(-math.sin(y),math.cos(y),0);up=(-math.sin(p)*math.cos(y),-math.sin(p)*math.sin(y),math.cos(p))
    dot=lambda a,b:sum(x*y for x,y in zip(a,b));th=math.tan(math.radians(55/2));tv=th/1.6
    needs=[]
    for corner in corners:
        rel=tuple(corner[i]-center[i] for i in range(3));depth=dot(rel,forward)
        needs.extend([abs(dot(rel,right))/th-depth,abs(dot(rel,up))/tv-depth])
    distance=max(needs)*1.14;position=tuple(center[i]-forward[i]*distance for i in range(3))
    camera=scene['GalleryOverviewCamera'];camera.set_actor_location(unreal.Vector(*position),False,False);camera.set_actor_rotation(unreal.Rotator(pitch=pitch,yaw=yaw,roll=0),False)
    unreal.EditorLevelLibrary.set_level_viewport_camera_info(camera.get_actor_location(),camera.get_actor_rotation())
    assert g.LEVELS.save_current_level();assert g.LEVELS.load_level(path)
    scene={a.get_actor_label():a for a in g.ACTORS.get_all_level_actors()}
    for r in models:
        b=g.actor_bounds(scene[r['label']]);assert abs(b['min'][2])<.02
        assert g.package_path(scene[r['label']].static_mesh_component.static_mesh)==r['mesh']
    for i,a in enumerate(models):
        for b in models[i+1:]:
            aa,bb=a['world_bounds_cm'],b['world_bounds_cm'];assert not all(aa['min'][k]<bb['max'][k] and bb['min'][k]<aa['max'][k] for k in (0,1))
    report['layout']='Ascending height from front to back; exact projected-bounds camera framing with 14 percent margin.' if category in ['Architecture','Environment'] else 'Native-scale rows; exact projected-bounds camera framing with 14 percent margin.'
    report['studio']['camera_fitted_to_all_bounds']=True;report['models']=models;file.write_text(json.dumps(report,indent=2))
assert g.LEVELS.load_level(g.REVIEW)
