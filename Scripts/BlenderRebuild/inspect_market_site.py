import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
rows=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        if not c.static_mesh:continue
        nearby=[]
        for i in range(c.get_instance_count()):
            t=c.get_instance_transform(i,world_space=True);p=t.translation
            if -50<p.x<450 and 400<p.y<950:nearby.append({'index':i,'pos':[p.x,p.y,p.z],'scale':str(t.scale3d)})
        if nearby:rows.append({'actor':a.get_actor_label(),'component':c.get_name(),'mesh':c.static_mesh.get_path_name(),'instances':nearby})
(root/'Saved/blender-market-site.json').write_text(json.dumps(rows,indent=2))
