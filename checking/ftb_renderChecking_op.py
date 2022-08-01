import bpy
from .ftb_renderCheckData import RenderCheckData
from bpy.app.handlers import persistent


def getCurrentSettings(currentSet: RenderCheckData()):
    """Takes in a RenderCheckData() instance and populates each field with the current values from the current project file"""
    # resolution and framerate
    currentSet.framerate = bpy.context.scene.render.fps
    currentSet.resX = bpy.context.scene.render.resolution_x
    currentSet.resY = bpy.context.scene.render.resolution_y
    currentSet.resPercent = bpy.context.scene.render.resolution_percentage

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

    return currentSet


def setFinalSettings(resFps=False, shadows=False, ao=False, overscan=False, outparams=False, burnIn=False, renderSingleLayer=False):
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


def countActiveViewLayers():
    count = 0
    for vLayer in bpy.context.scene.view_layers:
        if vLayer.use:
            count += 1

    return count


def invalidBoolCheck():
    """Report object names with bool modifiers that do not have Exact Solver and Self Intersection enabled.
    Returns:  invalidBoolList which contains all objects with invalid Booleans"""

    invalidBoolList = list()

    for obj in bpy.context.scene.objects:
        for mod in obj.modifiers:
            if mod.type == 'BOOLEAN':
                if not (mod.solver == 'EXACT' and mod.use_self):
                    invalidBoolList.append(obj.name)

    return invalidBoolList


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

    def execute(self, context):
        setFinalSettings(resFps=self.resFps, shadows=self.shadows, ao=self.ao, overscan=self.overscan, outparams=self.outparams, burnIn=self.burnIn, renderSingleLayer=self.renderSingleLayer)
        getCurrentSettings(currentSet=bpy.context.scene.ftbCurrentRenderSettings)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(FTB_OT_RenderCheckRefresh_op)
    bpy.utils.register_class(FTB_OT_RenderCheckSetSettings_op)
    bpy.app.handlers.load_pre.append(renderCheck_preLoad_handler)


def unregister():
    bpy.app.handlers.load_pre.remove(renderCheck_preLoad_handler)
    bpy.utils.unregister_class(FTB_OT_RenderCheckSetSettings_op)
    bpy.utils.unregister_class(FTB_OT_RenderCheckRefresh_op)
