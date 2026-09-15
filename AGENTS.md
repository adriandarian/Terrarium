# Terrarium

- Engine baseline: Unreal Engine 5.8.2; project descriptor: Terrarium.uproject.
- Blank Blueprint project. Gameplay and art direction are yet to be defined.
- Use bundled Unreal MCP with this project open. Discover toolsets first; call tools sequentially.
- Verify the connected editor belongs to Terrarium before editing through MCP.
- Keep MCP configuration project-local.
- Use Unreal editor tools to modify binary .uasset and .umap files.
- Keep generated Binaries, Intermediate, Saved and DerivedDataCache out of source control.
- Validate changes in the editor and report what was actually tested.
- Blender MCP setup and launch instructions: `Docs/BlenderMCP.md`.
- Use Blender Lab MCP 1.0.3 with the matching extension. Launch project Blender sessions with `Scripts/Open-Blender.ps1`; verify the scene's `terrarium_project` property before editing through Blender MCP. For manually opened sessions without that marker, verify the intended file and scene first.
