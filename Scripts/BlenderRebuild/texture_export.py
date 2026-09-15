"""Pack color-managed PNG8 maps for the verified Unreal atlas import path."""
import bpy,hashlib,json

def normalize_maps(scene, output, review, key):
    images={}
    for ob in scene.objects:
        if not ob.get('part'):continue
        for slot in ob.material_slots:
            mat=slot.material
            if mat and mat.use_nodes:
                for node in mat.node_tree.nodes:
                    if node.type=='TEX_IMAGE' and node.image:
                        for kind in ['BaseColor','Emission','Roughness']:
                            if node.image.name.split('.')[0]==key+'_'+kind:images[kind]=node.image
    changed=[]
    export_scene=None
    try:
        for kind,image in images.items():
            path=output/(key+'_'+kind+'.png')
            assert path.exists(),path
            if path.read_bytes()[24]!=16:continue
            if export_scene is None:
                export_scene=bpy.data.scenes.new(key+' texture export')
                settings=export_scene.render.image_settings
                settings.file_format='PNG';settings.color_mode='RGB';settings.color_depth='8'
                export_scene.view_settings.look='None';export_scene.view_settings.exposure=0;export_scene.view_settings.gamma=1
            before=hashlib.sha256(path.read_bytes()).hexdigest()
            export_scene.view_settings.view_transform='Raw' if kind=='Roughness' else 'Standard'
            image.save_render(str(path),scene=export_scene)
            assert path.read_bytes()[24]==8
            if image.packed_file:image.unpack(method='REMOVE')
            image.source='FILE';image.filepath_raw=str(path);image.reload();image.pack()
            changed.append({'map':kind,'before_sha256':before,'after_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bit_depth':8})
    finally:
        if export_scene:bpy.data.scenes.remove(export_scene)
    if changed:
        (review/'texture-export-conversion.json').write_text(json.dumps({'asset':key,'changes':changed,'color_transform':'Standard sRGB for BaseColor and Emission; Raw for non-color Roughness. Exposure 0, gamma 1, no look.','reason':'These PNG16 atlas imports sampled encoded RGB in Unreal despite srgb=true. PNG8 was verified through an RGBA32F shader readback.'},indent=2))
    return changed
