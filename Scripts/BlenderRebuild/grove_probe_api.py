import unreal
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
names=['create_render_target2d','draw_material_to_render_target','read_render_target_raw_pixel','read_render_target_pixel']
(root/'Saved/grove-render-api.txt').write_text('\n'.join(n+'\n'+str(getattr(unreal.RenderingLibrary,n).__doc__) for n in names))
