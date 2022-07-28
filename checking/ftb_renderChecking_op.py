import bpy
from dataclasses import dataclass
from bpy.app.handlers import persistent

@dataclass
class RenderCheckData:
    """A class that can contain all relevant render settings to compare against defaults for render check."""
    framerate : int = 50
    resX : int = 3840
    resY : int = 2160
    resPercent : int = 100

    casShadow : str = '4096'
    cubeShadow : str = '4096'
    highBitShadow : bool = True
    softShadow : bool = True

    useAo : bool = True
    aoDist : float = 0.5
    aoFactor : float = 1.0
    aoQuality :float = 1.0
    aoBentNormals : bool = True
    aoBounce : bool = True

    overscan : bool = True
    oversize : float = 5.0

    outFormat : str = 'OPEN_EXR_MULTILAYER'
    outColor : str = 'RGBA'
    outDepth : str = '32'
    outCodec : str = 'ZIP'


def getCurrentSettings(currentSet : RenderCheckData()):
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

    return currentSet

def setFinalSettings():
    """Set render settings to final settings"""

    # Generate new RenderCheckData instance with default settings
    defaultSet = RenderCheckData()

    # resolution, framerate
    bpy.context.scene.render.resolution_x = defaultSet.resX
    bpy.context.scene.render.resolution_y = defaultSet.resY
    bpy.context.scene.render.resolution_percentage = defaultSet.resPercent
    bpy.context.scene.render.fps = defaultSet.framerate

    # shadows
    bpy.context.scene.eevee.shadow_cascade_size = defaultSet.casShadow
    bpy.context.scene.eevee.shadow_cube_size = defaultSet.cubeShadow
    bpy.context.scene.eevee.use_shadow_high_bitdepth = defaultSet.highBitShadow
    bpy.context.scene.eevee.use_soft_shadows = defaultSet.softShadow

    # ambient occlusion
    bpy.context.scene.eevee.use_gtao = defaultSet.useAo
    bpy.context.scene.eevee.gtao_distance = defaultSet.aoDist
    bpy.context.scene.eevee.gtao_factor = defaultSet.aoFactor
    bpy.context.scene.eevee.gtao_quality = defaultSet.aoQuality
    bpy.context.scene.eevee.use_gtao_bent_normals = defaultSet.aoBentNormals
    bpy.context.scene.eevee.use_gtao_bounce = defaultSet.aoBounce

    # overscan
    bpy.context.scene.eevee.use_overscan = defaultSet.overscan
    bpy.context.scene.eevee.overscan_size = defaultSet.oversize

    # output settings
    bpy.context.scene.render.image_settings.file_format = defaultSet.outFormat
    bpy.context.scene.render.image_settings.color_mode = defaultSet.outColor
    bpy.context.scene.render.image_settings.color_depth = defaultSet.outDepth
    bpy.context.scene.render.image_settings.exr_codec = defaultSet.outCodec

def viewLayerCheck():
    """Check if more than one view layer exists, if not return False"""

    if (len(bpy.context.scene.view_layers) < 2):
        return False
    else:
        return True

def invalidBoolCheck():
    """Report objects with bool modifiers that do not have Exact Solver and Self Intersection enabled. 
    Returns list invalidBoolList which contains all objects with invalid Booleans"""

    invalidBoolList = list()

    for obj in bpy.context.scene.objects:
        for mod in obj.modifiers:
            if mod.type == 'BOOLEAN':
                if not (mod.solver == 'EXACT' and mod.use_self):
                    invalidBoolList.append(obj)

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

    # If the operator was not run at least once after startup, do not display any info
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

        # boolList = invalidBoolCheck()

        # if boolList:
        #     reportstring = "There are " + str(len(boolList)) + " objects with invalid booleans. Pls fix"
        #     self.report({'WARNING'}, reportstring)

        # else: self.report({'INFO'}, "chillin")
        self.__class__.ranOnce = True
        getCurrentSettings(currentSet=bpy.context.scene.ftbCurrentRenderSettings)

        
        return {'FINISHED'}


class FTB_OT_RenderCheckSetResolution_op(bpy.types.Operator):
    bl_idname = "utils.render_check_set_resolution"
    bl_label = "Set Final Resolution"
    bl_description = "Set resolution and framerate to final settings"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        return {'FINISHED'}

def register():
    bpy.utils.register_class(FTB_OT_RenderCheckRefresh_op)
    bpy.app.handlers.load_pre.append(renderCheck_preLoad_handler)
    

def unregister():
    bpy.app.handlers.load_pre.remove(renderCheck_preLoad_handler)
    bpy.utils.unregister_class(FTB_OT_RenderCheckRefresh_op)
    
