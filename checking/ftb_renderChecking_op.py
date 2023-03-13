import bpy

from bpy.types import Object
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

    # Find objects with booleans set to Fast missing self intersection setting
    # Only stores names instead of whole object references, to avoid issues when objects are deleted by the user
    currentSet.invalidBoolObjects = invalidBoolCheck()

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

    # Get objects that have nla strips and also an active action (this causes the nla strips to not work properly and breaks animation)
    # Only stores names instead of whole object references, to avoid issues when objects are deleted by the user
    currentSet.invalidNlaObjects = invalidNlaCheck()
    currentSet.invalid_data_transfer_objects = get_invalid_data_transfer_objects()

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

    return currentSet


def setFinalSettings(resFps=False, samples=False, shadows=False, ao=False, overscan=False, outparams=False, burnIn=False,
                     renderSingleLayer=False, colorManagement=False, filmTransparent=False, aovs=False):
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


def invalidBoolCheck():
    """Report object with bool modifiers that do not have Exact Solver and Self Intersection enabled.
    Returns:  invalidBoolList which contains all objects with invalid Booleans"""
    invalidBoolList = list()

    for obj in bpy.context.scene.objects:
        for mod in obj.modifiers:
            if mod.type != 'BOOLEAN':
                continue
            if not (mod.solver == 'EXACT' and mod.use_self):
                invalidBoolList.append(obj)
    return invalidBoolList


def invalidNlaCheck():
    """Report object names with NLA strips and active action. These objects will likely have broken animation.
    Returns invalidNlaList[str] which contains object names with invalid NLA setup"""
    invalidNlaList = list()
    for obj in bpy.context.scene.objects:
        if getattr(obj.animation_data, 'use_nla', False):
            if getattr(obj.animation_data, 'nla_tracks', False):
                if getattr(obj.animation_data, 'action', False):
                    invalidNlaList.append(obj.name)

    return invalidNlaList


def get_invalid_data_transfer_objects() -> list[Object]:
    """Returns a list of objects with Data Transfer modifiers that do not have a Source object set."""
    invalid_objects: list[Object] = []
    for obj in bpy.context.scene.objects:
        for modifier in obj.modifiers:
            if modifier.type != 'DATA_TRANSFER':
                continue
            if (modifier.object is None) or (modifier.show_render is False):
                invalid_objects.append(obj)
    return invalid_objects


# preLoad handler to clear old info from old file when loading new project file
@persistent
def renderCheck_preLoad_handler(dummy):
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

    aovs: bpy.props.BoolProperty(
        name="aovs",
        default=False
    )

    def execute(self, context):
        setFinalSettings(resFps=self.resFps, shadows=self.shadows, ao=self.ao, overscan=self.overscan,
                         outparams=self.outparams, burnIn=self.burnIn, renderSingleLayer=self.renderSingleLayer,
                         colorManagement=self.colorMangement, filmTransparent=self.filmTransparent,
                         aovs=self.aovs, samples=self.samples)

        getCurrentSettings(currentSet=bpy.context.scene.ftbCurrentRenderSettings)
        return {'FINISHED'}


class FTB_OT_SelectBooleanErrors_op(bpy.types.Operator):
    bl_idname = "utils.select_boolean_errors"
    bl_label = "Select Objects"
    bl_description = "Selects all objects with boolean issues"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene.ftbCurrentRenderSettings.invalidBoolObjects is not None

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        for obj in context.scene.ftbCurrentRenderSettings.invalidBoolObjects:
            obj.select_set(True)
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
           FTB_OT_SelectBooleanErrors_op)


def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.app.handlers.load_pre.append(renderCheck_preLoad_handler)


def unregister():
    bpy.app.handlers.load_pre.remove(renderCheck_preLoad_handler)

    for c in reversed(classes):
        bpy.utils.unregister_class(c)
