import bpy

from bpy.types import Object, Modifier
from .ftb_renderCheckData import RenderCheckData
from bpy.app.handlers import persistent


def getCurrentSettings(currentSet: RenderCheckData):
    """Takes in a RenderCheckData() instance and populates each field with the current values from the current project file"""
    # resolution and framerate
    currentSet.framerate = bpy.context.scene.render.fps
    currentSet.resX = bpy.context.scene.render.resolution_x
    currentSet.resY = bpy.context.scene.render.resolution_y
    currentSet.resPercent = bpy.context.scene.render.resolution_percentage

    # samples
    currentSet.renderSamples = bpy.context.scene.eevee.taa_render_samples

    # shadows
    currentSet.casShadow = bpy.context.scene.eevee.shadow_cascade_size
    currentSet.cubeShadow = bpy.context.scene.eevee.shadow_cube_size
    currentSet.highBitShadow = bpy.context.scene.eevee.use_shadow_high_bitdepth
    currentSet.softShadow = bpy.context.scene.eevee.use_soft_shadows

    # Ambient Occlusion
    currentSet.useAo = bpy.context.scene.eevee.use_gtao
    currentSet.aoDist = bpy.context.scene.eevee.gtao_distance
    currentSet.aoFactor = bpy.context.scene.eevee.gtao_factor
    currentSet.aoQuality = bpy.context.scene.eevee.gtao_quality
    currentSet.aoBentNormals = bpy.context.scene.eevee.use_gtao_bent_normals
    currentSet.aoBounce = bpy.context.scene.eevee.use_gtao_bounce

    # overscan
    currentSet.overscan = bpy.context.scene.eevee.use_overscan
    currentSet.oversize = bpy.context.scene.eevee.overscan_size

    # output settings
    currentSet.outFormat = bpy.context.scene.render.image_settings.file_format
    currentSet.outColor = bpy.context.scene.render.image_settings.color_mode
    currentSet.outDepth = bpy.context.scene.render.image_settings.color_depth
    currentSet.outCodec = bpy.context.scene.render.image_settings.exr_codec

    # Get state of burn in
    currentSet.isBurnInActive = bpy.context.scene.render.use_stamp

    # Get total view layer count
    currentSet.totalViewLayerCount = len(bpy.context.scene.view_layers)

    # Get active view layer count
    currentSet.activeViewLayerCount = countActiveViewLayers()

    # Get "Render Single Layer" setting
    currentSet.render_single_layer = bpy.context.scene.render.use_single_layer

    # Get "Film Transparent" setting
    currentSet.film_transparent = bpy.context.scene.render.film_transparent

    # simplify settings
    currentSet.simplify_subdiv_render = bpy.context.scene.render.simplify_subdivision_render

    # Get Color Management settings
    currentSet.cmDisplayDevice = bpy.context.scene.display_settings.display_device
    currentSet.cmViewTransform = bpy.context.scene.view_settings.view_transform
    currentSet.cmLook = bpy.context.scene.view_settings.look
    currentSet.cmExposure = bpy.context.scene.view_settings.exposure
    currentSet.cmGamma = bpy.context.scene.view_settings.gamma

    # Get AOVs
    aovKeyList = list()
    for aov in bpy.context.view_layer.aovs:
        aovKeyList.append(aov.name)

    aovValueList = list()
    for aov in bpy.context.view_layer.aovs:
        aovValueList.append(aov.type)

    # create dictionary from AOV data so they can be compared to default AOVs more easily
    currentSet.aovs = dict(zip(aovKeyList, aovValueList))

    # get if output path is UNC or not
    if len(bpy.context.scene.render.filepath) < 2:
        currentSet.uncOutput = False
    elif (bpy.context.scene.render.filepath[0] == "\\") and (bpy.context.scene.render.filepath[1] == "\\"):
        currentSet.uncOutput = True
    else:
        currentSet.uncOutput = False

    # get if current project file path is UNC or not
    projPath = bpy.data.filepath

    if len(projPath) < 2:
        currentSet.uncProject = False
    elif (projPath[0] == "\\") and (projPath[1] == "\\"):
        currentSet.uncProject = True
    else:
        currentSet.uncProject = False

    currentSet.invalidNlaObjects.clear()
    currentSet.invalidBoolObjects.clear()
    currentSet.invalid_data_transfer_objects.clear()
    currentSet.modifier_visibility_issues.clear()
    # loop over all objects to find errors
    for obj in bpy.context.view_layer.objects:
        if is_invalid_nla_object(obj):
            currentSet.invalidNlaObjects.append(obj)

        for modifier in obj.modifiers:
            if modifier.type not in ('BOOLEAN', 'DATA_TRANSFER', 'DISPLACE',
                                     'LATTICE', 'SOLIDIFY', 'SUBSURF', 'MULTIRES'):
                continue

            if is_invalid_bool_modifier(modifier):
                currentSet.invalidBoolObjects.append(obj)
            if is_invalid_data_transfer_modifier(modifier):
                currentSet.invalid_data_transfer_objects.append(obj)
            elif is_invalid_displace_lattice_solidify_modifier(modifier):
                currentSet.modifier_visibility_issues.append(obj)
            elif is_invalid_subdiv_modifier(modifier):
                currentSet.modifier_visibility_issues.append(obj)

    return currentSet


def setFinalSettings(
        resFps=False, samples=False, shadows=False, ao=False, overscan=False, outparams=False, burnIn=False,
        renderSingleLayer=False, colorManagement=False, filmTransparent=False, simplify=False, aovs=False):
    """
    Set render settings to final settings.
        resFps: Set resolution and framerate
        shadows: Set shadow resolution and shadow settings
        ao: Set ambient occlusion settings
        overscan: Set overscan
        outparams: Set output file format
        burnIn: Set burnIn Settings
    """

    # Generate new RenderCheckData instance with default settings
    defaultSet = RenderCheckData()

    # samples
    if samples:
        bpy.context.scene.eevee.taa_render_samples = defaultSet.renderSamples

    # resolution, framerate
    if resFps:
        bpy.context.scene.render.resolution_x = defaultSet.resX
        bpy.context.scene.render.resolution_y = defaultSet.resY
        bpy.context.scene.render.resolution_percentage = defaultSet.resPercent
        bpy.context.scene.render.fps = defaultSet.framerate

    # shadows
    if shadows:
        bpy.context.scene.eevee.shadow_cascade_size = defaultSet.casShadow
        bpy.context.scene.eevee.shadow_cube_size = defaultSet.cubeShadow
        bpy.context.scene.eevee.use_shadow_high_bitdepth = defaultSet.highBitShadow
        bpy.context.scene.eevee.use_soft_shadows = defaultSet.softShadow

    # ambient occlusion
    if ao:
        bpy.context.scene.eevee.use_gtao = defaultSet.useAo
        bpy.context.scene.eevee.gtao_distance = defaultSet.aoDist
        bpy.context.scene.eevee.gtao_factor = defaultSet.aoFactor
        bpy.context.scene.eevee.gtao_quality = defaultSet.aoQuality
        bpy.context.scene.eevee.use_gtao_bent_normals = defaultSet.aoBentNormals
        bpy.context.scene.eevee.use_gtao_bounce = defaultSet.aoBounce

    # overscan
    if overscan:
        bpy.context.scene.eevee.use_overscan = defaultSet.overscan
        bpy.context.scene.eevee.overscan_size = defaultSet.oversize

    # output settings
    if outparams:
        bpy.context.scene.render.image_settings.file_format = defaultSet.outFormat
        bpy.context.scene.render.image_settings.color_mode = defaultSet.outColor
        bpy.context.scene.render.image_settings.color_depth = defaultSet.outDepth
        bpy.context.scene.render.image_settings.exr_codec = defaultSet.outCodec

    # burn in
    if burnIn:
        bpy.context.scene.render.use_stamp = defaultSet.render_single_layer

    # render single layer
    if renderSingleLayer:
        bpy.context.scene.render.use_single_layer = defaultSet.render_single_layer

    # color mangement
    if colorManagement:
        bpy.context.scene.display_settings.display_device = defaultSet.cmDisplayDevice
        bpy.context.scene.view_settings.view_transform = defaultSet.cmViewTransform
        bpy.context.scene.view_settings.look = defaultSet.cmLook
        bpy.context.scene.view_settings.exposure = defaultSet.cmExposure
        bpy.context.scene.view_settings.gamma = defaultSet.cmGamma

    # transparent background
    if filmTransparent:
        bpy.context.scene.render.film_transparent = defaultSet.film_transparent

    # simplify default settings
    if simplify:
        bpy.context.scene.render.simplify_subdivision_render = defaultSet.simplify_subdiv_render

    # aovs
    if aovs:
        cs = getCurrentSettings(currentSet=bpy.context.scene.ftbCurrentRenderSettings)

        for key in defaultSet.aovs:
            if key in cs.aovs:
                if cs.aovs[key] is not defaultSet.aovs[key]:
                    bpy.context.view_layer.aovs[key].type = defaultSet.aovs[key]

            else:
                newLayer = bpy.context.view_layer.aovs.add()
                newLayer.name = key
                newLayer.type = defaultSet.aovs[key]


def countActiveViewLayers():
    count = 0
    for vLayer in bpy.context.scene.view_layers:
        if vLayer.use:
            count += 1

    return count


def is_invalid_bool_modifier(modifier: bpy.types.BooleanModifier) -> bool:
    """
    Returns True if boolean modifier not uses solver EXACT, not use self and show viewport or show render are off
    """
    if modifier.type != 'BOOLEAN':
        return False
    return not (modifier.solver == 'EXACT' and modifier.use_self) or not (
        modifier.show_viewport and modifier.show_render)


def is_invalid_nla_object(object: Object) -> bool:
    """
    Returns True if object has an active action on top of NLA-track. These objects will likely have broken animation.
    """
    if getattr(object.animation_data, 'use_nla', False):
        if getattr(object.animation_data, 'nla_tracks', False):
            if getattr(object.animation_data, 'action', False):
                return True

    return False


def is_invalid_data_transfer_modifier(modifier: bpy.types.DataTransferModifier) -> bool:
    """Returns True if data transfer modifier has no valid source object set."""
    if modifier.type != 'DATA_TRANSFER':
        return False
    return (modifier.object is None) or (modifier.show_render is False)


def is_invalid_displace_lattice_solidify_modifier(modifier: Modifier) -> bool:
    """
    Returns True if modifier is enabled in render but not in viewport. 
    If the modifier is not rendered, it also disables the modifier in viewport  
    """
    if modifier.type not in ('DISPLACE', 'LATTICE', 'SOLIDIFY', 'MULTIRES'):
        return False
    # ignore the modifier if show_render is disabled and disable show_viewport
    if not modifier.show_render:
        modifier.show_viewport = modifier.show_render
        return False

    return not (modifier.show_viewport and modifier.show_render)


def is_invalid_subdiv_modifier(modifier: bpy.types.SubsurfModifier) -> bool:
    """Returns True if render and viewport levels are not equal."""
    if modifier.type != 'SUBSURF':
        return False
    return modifier.render_levels != modifier.levels


@persistent
def renderCheck_preLoad_handler(dummy):
    """preLoad handler to clear old info from old file when loading new project file"""
    FTB_OT_RenderCheckRefresh_op.ranOnce = False
    return {'FINISHED'}


class FTB_OT_RenderCheckRefresh_op(bpy.types.Operator):
    bl_idname = "utils.render_check_refresh"
    bl_label = "Render Check"
    bl_description = "Run automated tests to prepare for rendering"
    bl_options = {"REGISTER", "UNDO"}

    # If the operator was not run at least once after startup, do not display any info to avoid null references from old data that has already been freed
    ranOnce = False

    # should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object

        if not obj:
            return True

        if obj:
            if obj.mode == "OBJECT":
                return True

        return False

    def execute(self, context):
        self.__class__.ranOnce = True
        getCurrentSettings(currentSet=bpy.context.scene.ftbCurrentRenderSettings)

        return {'FINISHED'}


class FTB_OT_RenderCheckSetSettings_op(bpy.types.Operator):
    bl_idname = "utils.render_check_set_settings"
    bl_label = "Set Final settings"
    bl_description = "Set render settings to final settings"
    bl_options = {"REGISTER", "UNDO"}

    resFps: bpy.props.BoolProperty(
        name='resFps',
        default=False
    )

    samples: bpy.props.BoolProperty(
        name="samples",
        default=False
    )

    shadows: bpy.props.BoolProperty(
        name='shadows',
        default=False
    )

    ao: bpy.props.BoolProperty(
        name='ao',
        default=False
    )

    overscan: bpy.props.BoolProperty(
        name='overscan',
        default=False
    )
    outparams: bpy.props.BoolProperty(
        name='outparams',
        default=False
    )

    burnIn: bpy.props.BoolProperty(
        name='burnIn',
        default=False
    )

    renderSingleLayer: bpy.props.BoolProperty(
        name='renderSingleLayer',
        default=False
    )

    colorMangement: bpy.props.BoolProperty(
        name='colorMangement',
        default=False
    )

    filmTransparent: bpy.props.BoolProperty(
        name="filmTransparent",
        default=False
    )

    simplify: bpy.props.BoolProperty(
        name="Simplify",
        default=False
    )

    aovs: bpy.props.BoolProperty(
        name="aovs",
        default=False
    )

    def execute(self, context):
        setFinalSettings(resFps=self.resFps, shadows=self.shadows, ao=self.ao, overscan=self.overscan,
                         outparams=self.outparams, burnIn=self.burnIn, renderSingleLayer=self.renderSingleLayer,
                         colorManagement=self.colorMangement, filmTransparent=self.filmTransparent,
                         simplify=self.simplify, aovs=self.aovs, samples=self.samples)

        getCurrentSettings(currentSet=bpy.context.scene.ftbCurrentRenderSettings)
        return {'FINISHED'}


class FTB_OT_FixBooleanErrors_op(bpy.types.Operator):
    bl_idname = "utils.fix_boolean_errors"
    bl_label = "Fix Boolean Issues"
    bl_description = "Fixes all Boolean issues compromising final visuals"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene.ftbCurrentRenderSettings.invalidBoolObjects is not None

    def execute(self, context):
        for obj in context.scene.ftbCurrentRenderSettings.invalidBoolObjects:
            for modifier in obj.modifiers:
                if modifier.type != 'BOOLEAN':
                    continue
                modifier.show_viewport = True
                modifier.show_render = True
                modifier.solver = 'EXACT'
                modifier.use_self = True

        bpy.ops.utils.render_check_refresh()
        return {'FINISHED'}


class FTB_OT_FixModifierVisiblityIssues_op(bpy.types.Operator):
    bl_idname = "utils.fix_modifier_visiblity_issues"
    bl_label = "Fix Modifier Visibility Issues"
    bl_description = "Fixes all modifier related visibilty issues compromising final render results"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene.ftbCurrentRenderSettings.modifier_visibility_issues is not None

    def execute(self, context):
        faulty_objects = context.scene.ftbCurrentRenderSettings.modifier_visibility_issues
        for obj in faulty_objects:
            for modifier in obj.modifiers:
                if modifier.type not in ('BOOLEAN', 'DATA_TRANSFER', 'DISPLACE', 'LATTICE', 'SOLIDIFY', 'SUBSURF'):
                    continue
                if modifier.type == 'SUBSURF':
                    modifier.levels = modifier.render_levels

                modifier.show_viewport = modifier.show_render

        bpy.ops.utils.render_check_refresh()
        return {'FINISHED'}


class FTB_OT_SelectDataTransferErrors_op(bpy.types.Operator):
    bl_idname = "utils.select_data_transfer_errors"
    bl_label = "Select Objects"
    bl_description = "Selects all objects with Data Transfer issues"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene.ftbCurrentRenderSettings.invalid_data_transfer_objects is not None

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        for obj in context.scene.ftbCurrentRenderSettings.invalid_data_transfer_objects:
            obj.select_set(True)
        return {'FINISHED'}


classes = (FTB_OT_RenderCheckRefresh_op, FTB_OT_RenderCheckSetSettings_op, FTB_OT_SelectDataTransferErrors_op,
           FTB_OT_FixBooleanErrors_op, FTB_OT_FixModifierVisiblityIssues_op)


def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.app.handlers.load_pre.append(renderCheck_preLoad_handler)


def unregister():
    bpy.app.handlers.load_pre.remove(renderCheck_preLoad_handler)

    for c in reversed(classes):
        bpy.utils.unregister_class(c)
