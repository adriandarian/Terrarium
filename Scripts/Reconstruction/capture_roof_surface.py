"""Native matched roof swatch front/back and source-oriented top captures."""
import json,time
from pathlib import Path
import unreal
assert Path(unreal.Paths.get_project_file_path()).name=='Terrarium.uproject'
root=Path(unreal.Paths.project_dir())
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if '/Reconstruction/Maps/ReviewStage' not in str(levels.get_current_level()):
    assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages(),'Preserve unsaved editor maps before capture'
    assert levels.load_level('/Game/Terrarium/Reconstruction/Maps/ReviewStage')
key=globals().get('ROOF_KEY','cottage_roof_tile_v5')
assert key in ('cottage_roof_tile_v5','cottage_roof_tile_v6_candidate')
name='SM_Recon_'+key+'_R2'
requests=[]
for view,yaw,pitch in [('front',115,-55),('back',295,-55),('top',270,-90)]:
    request={'asset':'/Game/Terrarium/Reconstruction/Meshes/'+name,'name':name+'-'+view,
             'yaw':yaw,'pitch':pitch,'resolution':1254}
    if view=='top':request.update(projection='orthographic',ortho_width=106)
    requests.append(request)
state={'index':0,'next':time.monotonic()+3}
code=(root/'Scripts/Reconstruction/capture.py').read_text()
def tick(delta):
    if time.monotonic()<state['next']:return
    try:
        request=requests[state['index']]
        (root/'Saved/reconstruction-capture.json').write_text(json.dumps(request))
        exec(compile(code,'capture.py','exec'),{'__name__':'__main__'})
        state['index']+=1;state['next']=time.monotonic()+2
        if state['index']==len(requests):
            unreal.unregister_slate_post_tick_callback(state['handle'])
            (root/'Docs/Reconstruction/Renders'/(name+'-capture.json')).write_text(json.dumps({'views':requests,'lighting':'unchanged saved ReviewStage'},indent=2))
            unreal.log('ROOF_SURFACE_CAPTURES_COMPLETE')
    except Exception:
        unreal.unregister_slate_post_tick_callback(state['handle']);raise
state['handle']=unreal.register_slate_post_tick_callback(tick)
