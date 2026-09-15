# Blender MCP for Terrarium

Installed [Blender Lab MCP](https://www.blender.org/lab/mcp-server/), pinned to release **1.0.3**, matching the user's enabled Blender Lab MCP extension in Blender **5.2.1 LTS**. This replaces the earlier community ahujasid integration.

The MCP entry is in `.codex/config.toml` alongside Unreal MCP. Its server runs from `Saved/BlenderMCP/lab-venv`; the release source, uv executable, caches, and logs also live under the ignored `Saved/BlenderMCP` folder. The Blender extension is the user's installation under their Blender preferences, with Auto Start enabled. No global Codex MCP entry is used. Earlier community runtime files remain inactive under Saved; the old community listener was stopped.

## Use

From the Terrarium project directory:

```powershell
.\Scripts\Open-Blender.ps1
# Or open an existing source asset:
.\Scripts\Open-Blender.ps1 -BlendFile .\SourceAssets\example.blend
```

Blender can be opened normally with the Blender Lab MCP extension enabled and Auto Start checked. Its preferences should show **Server is running**, using localhost port **9876**. Keep that Blender window running while using MCP. Do not enable the earlier community add-on on the same port.

The optional project launcher uses the user's installed extension and adds a `terrarium_project` scene property. It refuses to launch if port 9876 is occupied. When connecting to a manually opened session, check the file path and intended scene before editing; such sessions may not have the project marker.

The launcher also recovers an installed but inactive Lab extension after an editor restart. If its repository preference is missing, it registers the existing `lab_blender_org` directory for that process, enables the matching installed extension, and uses online mode so the local MCP bridge can start. It does not download an extension or save global Blender preferences. A legacy library-only source is opened into its named Terrarium scene when available. Current rebuilt asset files are being repackaged as normal Blender projects and independently reopened; see `Docs/BlenderRebuild/project-packaging-verification.json` for exact coverage.

Reload the Codex MCP servers (or restart Codex) after adding the configuration. Project-local configuration is supported for trusted projects; see [OpenAI's MCP documentation](https://developers.openai.com/codex/mcp/). The old standalone `codex-cli 0.92.0` installed on this machine did not discover this project entry with `codex mcp get blender`; the server was instead validated with the MCP SDK using the exact project configuration. Desktop tool discovery must be checked after reloading.

## Reinstall after clearing Saved

```powershell
.\Scripts\Install-BlenderMCP.ps1
```

The installer obtains uv from Astral's official installer, downloads Blender Lab's **blender-1.0.3.mcpb** release, verifies its recorded SHA-256, and installs the included server source into a local Python environment. It does not install from the similarly named community PyPI package. Install or update the Blender Lab extension through Blender's preferences separately. The scripts default to `C:\Program Files\Blender Foundation\Blender 5.2`; pass `-BlenderPython` to the installer or `-BlenderPath` to the launcher for another installation. If moving this project, update the absolute project paths in `.codex/config.toml`.

## Validation performed

- Confirmed the user's Blender Lab extension is installed, enabled, and responding in Blender 5.2.1.
- Initialized a real MCP stdio session using the command and environment from `.codex/config.toml`.
- Discovered 26 tools and successfully called `get_objects_summary` on the running Blender editor.
- Read the Blender version, process ID, file path, and enabled extension through `execute_blender_code`. The connected user window was process 30324 with an unsaved file and no project marker.
- The default Cube, Camera, and Light were present. No Unreal assets or maps were edited.

Current verification output: `Saved/BlenderMCP/lab-verification.json`. The earlier `verification.json` describes the superseded community installation. The updated launcher was checked for syntax but not used to launch another window because the user's editor was already running.
