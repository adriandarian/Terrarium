"""Continuous WORLD-space river pigment; removes all per-tile color gradients.

Applies only to current-level river components after placement.flush(). The
existing native closed mesh and tiny raised glints remain unchanged. Surface
color never reads UVs, object position, vertex colors, or a tile depth variant.
"""
import unreal

LIB = unreal.MaterialEditingLibrary
PATH = '/Game/Terrarium/Materials/M_Pass7_ContinuousRiver'


def _node(mat, kind, x, y):
    return LIB.create_material_expression(mat, kind, x, y)


def _connect(source, target, pin):
    if pin == 'Input':
        pin = LIB.get_material_expression_input_names(target)[0]
    output = LIB.get_material_expression_output_names(source)[0]
    assert LIB.connect_material_expressions(source, output, target, pin)


def _pigment(mat, rgb, x, y):
    node = _node(mat, unreal.MaterialExpressionConstant3Vector, x, y)
    node.set_editor_property('constant', unreal.LinearColor(*rgb, 1))
    return node


def _noise(mat, position, scale, low, high, x, y):
    node = _node(mat, unreal.MaterialExpressionNoise, x, y)
    for key, value in [('scale', scale), ('levels', 2), ('quality', 1),
                       ('output_min', low), ('output_max', high)]:
        node.set_editor_property(key, value)
    _connect(position, node, 'Input')
    return node


def material():
    if unreal.EditorAssetLibrary.does_asset_exist(PATH):
        mat = unreal.load_asset(PATH)
        LIB.delete_all_material_expressions(mat)
    else:
        mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            'M_Pass7_ContinuousRiver', '/Game/Terrarium/Materials',
            unreal.Material, unreal.MaterialFactoryNew())
    assert mat
    mat.set_editor_property('two_sided', False)
    position = _node(mat, unreal.MaterialExpressionWorldPosition, -1400, 0)
    pools = _noise(mat, position, .0018, .12, .88, -1150, -160)
    fine = _noise(mat, position, .038, .91, 1.07, -1150, 70)
    # Linear colors: relatively dark blue-teal pools and restrained turquoise.
    deep = _pigment(mat, (.013, .090, .102), -1130, -480)
    shallow = _pigment(mat, (.033, .205, .183), -1130, -340)
    base = _node(mat, unreal.MaterialExpressionLinearInterpolate, -800, -270)
    _connect(deep, base, 'A')
    _connect(shallow, base, 'B')
    _connect(pools, base, 'Alpha')
    grain = _node(mat, unreal.MaterialExpressionMultiply, -550, -180)
    _connect(base, grain, 'A')
    _connect(fine, grain, 'B')

    # The water plane is Z=1cm; only the existing tiny modeled glints rise
    # above 1.35cm. Their upper surfaces receive a soft pale green accent.
    z = _node(mat, unreal.MaterialExpressionComponentMask, -1130, 360)
    for key, value in [('r', False), ('g', False), ('b', True), ('a', False)]:
        z.set_editor_property(key, value)
    _connect(position, z, 'Input')
    rise = _node(mat, unreal.MaterialExpressionSubtract, -900, 360)
    rise.set_editor_property('const_b', 1.15)
    _connect(z, rise, 'A')
    amount = _node(mat, unreal.MaterialExpressionMultiply, -700, 360)
    amount.set_editor_property('const_b', .75)
    _connect(rise, amount, 'A')
    mask = _node(mat, unreal.MaterialExpressionClamp, -500, 360)
    _connect(amount, mask, 'Input')
    glint = _pigment(mat, (.14, .32, .28), -480, 50)
    result = _node(mat, unreal.MaterialExpressionLinearInterpolate, -190, -80)
    _connect(grain, result, 'A')
    _connect(glint, result, 'B')
    _connect(mask, result, 'Alpha')
    assert LIB.connect_material_property(result, '', unreal.MaterialProperty.MP_BASE_COLOR)
    for prop, value, y in [(unreal.MaterialProperty.MP_ROUGHNESS, .88, 260),
                            (unreal.MaterialProperty.MP_SPECULAR, .08, 370)]:
        node = _node(mat, unreal.MaterialExpressionConstant, -170, y)
        node.set_editor_property('r', value)
        assert LIB.connect_material_property(node, '', prop)
    LIB.recompile_material(mat)
    assert unreal.EditorAssetLibrary.save_loaded_asset(mat)
    return mat


def apply():
    assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert '/HomesteadFidelity.' in str(levels.get_current_level())
    mat = material()
    report = {'material': PATH, 'components': 0, 'instances': 0,
              'base_color_coordinates': 'absolute world position',
              'uses_vertex_or_tile_local_color': False}
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for actor in actors.get_all_level_actors():
        for component in actor.get_components_by_class(unreal.StaticMeshComponent):
            mesh = component.static_mesh
            if not mesh or not mesh.get_path_name().startswith('/Game/Terrarium/Meshes/'):
                continue
            if mesh.get_name() not in ('SM_WaterTile_v4', 'SM_WaterShallow_v4', 'SM_WaterDeep_v4'):
                continue
            count = (component.get_instance_count()
                     if isinstance(component, unreal.InstancedStaticMeshComponent) else 1)
            if not count:
                continue
            component.set_material(0, mat)
            assert component.get_material(0) == mat
            report['components'] += 1
            report['instances'] += count
    assert report['instances'] > 0, 'No pass7 river instances received material'
    unreal.log('PASS7_CONTINUOUS_RIVER '+str(report))
    return report
