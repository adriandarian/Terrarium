"""Native matte world-space surface treatment, scoped to the current scene.

Material overrides belong to components in HomesteadFidelity, never the shared
mesh or foliage-type assets. Water, plant and traveler palettes stay independent.
Call apply() after placement.flush(), before saving/capturing the composed map.
"""
import unreal


ROOT = '/Game/Terrarium/Materials'
LIB = unreal.MaterialEditingLibrary


def _node(material, kind, x, y):
    return LIB.create_material_expression(material, kind, x, y)


def _connect(source, destination, pin):
    if pin == 'Input':
        pin = LIB.get_material_expression_input_names(destination)[0]
    output = LIB.get_material_expression_output_names(source)[0]
    assert LIB.connect_material_expressions(source, output, destination, pin)


def _multiply(material, a, b, x, y):
    result = _node(material, unreal.MaterialExpressionMultiply, x, y)
    _connect(a, result, 'A')
    _connect(b, result, 'B')
    return result


def _noise(material, position, scale, low, high, x, y):
    noise = _node(material, unreal.MaterialExpressionNoise, x, y)
    for key, value in [('scale', scale), ('levels', 1), ('quality', 1),
                       ('output_min', low), ('output_max', high)]:
        noise.set_editor_property(key, value)
    # Explicit world coordinates continue across every rotated 72 cm tile.
    _connect(position, noise, 'Input')
    return noise


def _pigment(material, rgb, x, y):
    color = _node(material, unreal.MaterialExpressionConstant3Vector, x, y)
    color.set_editor_property('constant', unreal.LinearColor(*rgb, 1))
    return color


def _patch_mask(material, position, scale, threshold, width, x, y):
    """Irregular two-octave islands with a narrow but antialiased boundary."""
    noise = _noise(material, position, scale, 0, 1, x, y)
    noise.set_editor_property('levels', 2)
    subtract = _node(material, unreal.MaterialExpressionSubtract, x+190, y)
    subtract.set_editor_property('const_b', threshold)
    _connect(noise, subtract, 'A')
    divide = _node(material, unreal.MaterialExpressionDivide, x+380, y)
    divide.set_editor_property('const_b', width)
    _connect(subtract, divide, 'A')
    clamp = _node(material, unreal.MaterialExpressionClamp, x+570, y)
    _connect(divide, clamp, 'Input')
    return clamp


def _blend(material, first, second, mask, x, y):
    result = _node(material, unreal.MaterialExpressionLinearInterpolate, x, y)
    _connect(first, result, 'A')
    _connect(second, result, 'B')
    _connect(mask, result, 'Alpha')
    return result


def _ground_pigment(material, position):
    # Retain a faint angular influence without shading every 17 cm square.
    # Broad colors use 84% continuous coordinates and only 16% grid influence;
    # the prior fully snapped coordinates exposed a mechanical checkerboard.
    divide = _node(material, unreal.MaterialExpressionDivide, -2100, -950)
    divide.set_editor_property('const_b', 17.0)
    _connect(position, divide, 'A')
    floor = _node(material, unreal.MaterialExpressionFloor, -1900, -950)
    _connect(divide, floor, 'Input')
    offset = _node(material, unreal.MaterialExpressionAdd, -1700, -950)
    offset.set_editor_property('const_b', .43)
    _connect(floor, offset, 'A')
    snapped = _node(material, unreal.MaterialExpressionMultiply, -1500, -950)
    snapped.set_editor_property('const_b', 17.0)
    _connect(offset, snapped, 'A')

    painted_position = _node(material, unreal.MaterialExpressionLinearInterpolate,
                             -1290, -1080)
    painted_position.set_editor_property('const_alpha', .16)
    _connect(position, painted_position, 'A')
    _connect(snapped, painted_position, 'B')

    # Closely related pigments keep the field muted: the previous high-valued
    # dry highlights and narrow masks produced conspicuous camouflage blobs.
    earth = _pigment(material, (.139, .137, .048), -1100, -900)
    moss = _pigment(material, (.151, .181, .036), -1100, -790)
    dry = _pigment(material, (.169, .182, .051), -1100, -680)
    main = _patch_mask(material, painted_position, .0045, .25, .50, -1400, -550)
    meadow = _blend(material, earth, moss, main, -520, -820)
    accents = _patch_mask(material, painted_position, .013, .43, .44, -1400, -370)
    color = _blend(material, meadow, dry, accents, -290, -690)
    # Fivefold reduction in per-cell amplitude removes the dominant checker.
    # Larger pigment regions carry detail; the tiny cells are subordinate.
    cells = _noise(material, snapped, .113, .97, 1.03, -1100, -190)
    broad = _noise(material, position, .0025, .94, 1.07, -1100, -50)
    grain = _multiply(material, cells, broad, -550, -190)

    # Sparse narrow pigment traces suggest grass/soil striations. A stretched
    # continuous coordinate field avoids painting one line on every grid cell.
    stretch = _pigment(material, (.34, 2.9, 1), -1420, 170)
    line_position = _multiply(material, position, stretch, -1230, 200)
    line_mask = _patch_mask(material, line_position, .033, .72, .19,
                            -1050, 420)
    line_dark = _node(material, unreal.MaterialExpressionMultiply, -80, -630)
    line_dark.set_editor_property('const_b', .92)
    _connect(color, line_dark, 'A')
    color = _blend(material, color, line_dark, line_mask, 100, -650)
    color = _multiply(material, color, grain, -70, -450)
    # Unequal, jittered pigment islands break up the continuous noise without
    # exposing a rectangular tile grid. All distances are world centimeters.
    patches = _node(material, unreal.MaterialExpressionCustom, 360, -450)
    patches.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    inputs = []
    for name in ('World', 'Pigment'):
        pin = unreal.CustomInput()
        pin.set_editor_property('input_name', name)
        inputs.append(pin)
    patches.set_editor_property('inputs', inputs)
    patches.set_editor_property('code', '''
float2 p = World.xy / 27.0;
float2 cell = floor(p);
float nearest = 100.0;
float selected = 0.0;
for (int y = -1; y <= 1; ++y) {
    for (int x = -1; x <= 1; ++x) {
        float2 id = cell + float2(x, y);
        float2 jitter = frac(sin(float2(dot(id,float2(127.1,311.7)),
                                        dot(id,float2(269.5,183.3)))) * 43758.5453);
        float2 d = id + .12 + .76 * jitter - p;
        float distance = dot(d,d);
        if (distance < nearest) {
            nearest = distance;
            selected = jitter.x;
        }
    }
}
// Low-amplitude angular patches remain subordinate to the broad meadow color.
float shade = lerp(.84, 1.14, selected);
float3 tint = lerp(float3(1.025, .985, .91), float3(.96, 1.02, 1.04), selected);
return Pigment * shade * tint;
''')
    assert LIB.connect_material_expressions(position, '', patches, 'World')
    assert LIB.connect_material_expressions(color, '', patches, 'Pigment')
    return patches


def _material(name, broad_scale, broad_range, fine_scale, fine_range,
              ground=False):
    path = ROOT + '/' + name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        material = unreal.load_asset(path)
        LIB.delete_all_material_expressions(material)
    else:
        material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            name, ROOT, unreal.Material, unreal.MaterialFactoryNew())
    assert material
    material.set_editor_property('two_sided', False)
    vertex = _node(material, unreal.MaterialExpressionVertexColor, -1000, -280)
    position = _node(material, unreal.MaterialExpressionWorldPosition, -1230, 120)
    color = vertex
    if ground:
        result = _ground_pigment(material, position)
    else:
        broad = _noise(material, position, broad_scale, *broad_range, -960, 140)
        fine = _noise(material, position, fine_scale, *fine_range, -960, 360)
        grain = _multiply(material, broad, fine, -660, 130)
        result = _multiply(material, color, grain, -380, -100)
    assert LIB.connect_material_property(result, '',
                                         unreal.MaterialProperty.MP_BASE_COLOR)
    for prop, value, y in [(unreal.MaterialProperty.MP_ROUGHNESS, .97, 250),
                            (unreal.MaterialProperty.MP_SPECULAR, .055, 350)]:
        constant = _node(material, unreal.MaterialExpressionConstant, -380, y)
        constant.set_editor_property('r', value)
        assert LIB.connect_material_property(constant, '', prop)
    LIB.recompile_material(material)
    assert unreal.EditorAssetLibrary.save_loaded_asset(material)
    return material


def _family(name):
    if name.startswith('SM_PathTile_'):
        return 'Path'
    if name.startswith('SM_MeadowTile_'):
        return 'Ground'
    if name.startswith(('SM_CliffColumn_', 'SM_RockCluster', 'SM_ShoreOutcrop',
                        'SM_StoneStairs')):
        return 'Stone'
    if name.startswith(('SM_Cottage_', 'SM_Shed_', 'SM_PlankBridge_',
                        'SM_FencePost', 'SM_FenceRail', 'SM_GardenWell_',
                        'SM_LanternPost', 'SM_PathTile_', 'SM_Path_')):
        return 'Details'
    return None


def apply():
    """Return assignment evidence; the caller owns saving the composed level."""
    assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert '/HomesteadFidelity.' in str(levels.get_current_level())
    materials = {
        'Ground': _material('M_Pass7_Ground', .0025, (.84, 1.13),
                            .018, (.88, 1.12), ground=True),
        'Stone': _material('M_Pass7_Stone', .019, (.70, 1.12),
                           .10, (.68, 1.20)),
        'Details': _material('M_Pass7_Details', .017, (.95, 1.055),
                             .105, (.975, 1.025)),
        'Path': _material('M_Pass7_Path', .009, (.74, 1.05),
                         .09, (.88, 1.13)),
    }
    report = {key: {'material': value.get_path_name(), 'components': 0,
                    'instances': 0, 'meshes': set()}
              for key, value in materials.items()}
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for actor in actors.get_all_level_actors():
        for component in actor.get_components_by_class(unreal.StaticMeshComponent):
            mesh = component.static_mesh
            if not mesh or not mesh.get_path_name().startswith('/Game/Terrarium/Meshes/'):
                continue
            family = _family(mesh.get_name())
            if family is None:
                continue
            instances = (component.get_instance_count()
                         if isinstance(component, unreal.InstancedStaticMeshComponent)
                         else 1)
            if not instances:
                continue
            component.set_material(0, materials[family])
            assert component.get_material(0) == materials[family]
            report[family]['components'] += 1
            report[family]['instances'] += instances
            report[family]['meshes'].add(mesh.get_name())
    for data in report.values():
        data['meshes'] = sorted(data['meshes'])
    assert report['Ground']['instances'] > 0, 'No meadow components were treated'
    assert report['Stone']['instances'] > 0, 'No rock components were treated'
    assert report['Details']['instances'] > 0, 'No building components were treated'
    unreal.log('PASS7_SURFACE_TREATMENT ' + str(report))
    return report
