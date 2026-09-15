"""Identify a Terrarium Blender session using the user's Blender Lab extension."""
from pathlib import Path

import bpy
import addon_utils
import os

project = Path(__file__).resolve().parents[1]
if "bl_ext.lab_blender_org.mcp" not in bpy.context.preferences.addons:
    # The installed extension may be disabled in a recovered editor session.
    # Enable it for this project process only; do not rewrite global preferences.
    repos=bpy.context.preferences.extensions.repos
    if not any(r.module=='lab_blender_org' for r in repos):
        installed=Path(os.environ['APPDATA'])/'Blender Foundation/Blender/5.2/extensions/lab_blender_org'
        if not (installed/'mcp/blender_manifest.toml').is_file():
            raise RuntimeError('Blender Lab MCP is not installed in the expected extension folder.')
        repos.new(name='Blender Lab',module='lab_blender_org',custom_directory=str(installed),remote_url='https://lab.blender.org/')
    # Lab's register() reads its preferences immediately, so create the in-memory
    # preferences entry as well. No save_userpref call is made.
    addon_utils.enable("bl_ext.lab_blender_org.mcp", default_set=True, persistent=True)
    if "bl_ext.lab_blender_org.mcp" not in bpy.context.preferences.addons:
        raise RuntimeError("The installed Blender Lab MCP extension could not be enabled.")
if bpy.data.filepath:
    wanted='Terrarium_'+Path(bpy.data.filepath).stem
    scene=bpy.data.scenes.get(wanted)
    if scene is None and Path(bpy.data.filepath).is_relative_to(project/'SourceAssets/Blender'):
        with bpy.data.libraries.load(bpy.data.filepath,link=False) as (data_from,data_to):
            if wanted in data_from.scenes:data_to.scenes=[wanted]
        scene=bpy.data.scenes.get(wanted)
    if scene and scene.get('terrarium_project')==str(project):
        bpy.context.window.scene=scene
bpy.context.scene["terrarium_project"] = str(project)
print(f"TERRARIUM_BLENDER_SESSION {project}", flush=True)
# Blender Lab's Auto Start preference starts the server after initialization.
