import bpy
from bpy.types import Operator


class FTB_OT_DefaultRenderSettings_Op(Operator):
    bl_idname = "scene.default_render_settings"
    bl_label = "Set Default Settings"
    bl_description = "Set render settings to project defaults"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        wm = bpy.context.window_manager
        if any([wm.bsetShadows, wm.bsetResolution, wm.bsetFramerate, wm.bsetEngine]):
            return True
        else:
            return False

    def execute(self, context):
        wm = bpy.context.window_manager
        messageString = "Setup successful for:"

        if wm.bsetShadows:
            bpy.context.scene.eevee.shadow_cascade_size = '4096'
            bpy.context.scene.eevee.shadow_cube_size = '4096'
            bpy.context.scene.eevee.use_shadow_high_bitdepth = True
            bpy.context.scene.eevee.use_soft_shadows = True

            # Ambient Occlusion Settings

            bpy.context.scene.eevee.use_gtao = True
            bpy.context.scene.eevee.gtao_distance = 0.5
            bpy.context.scene.eevee.gtao_factor = 1
            bpy.context.scene.eevee.gtao_quality = 1
            bpy.context.scene.eevee.use_gtao_bent_normals = True
            bpy.context.scene.eevee.use_gtao_bounce = True

            # Overscan to avoid AO fading at screen edge

            bpy.context.scene.eevee.use_overscan = True
            bpy.context.scene.eevee.overscan_size = 5

            messageString += " Shadows, Ambient Occlusion,"

        if wm.bsetResolution:
            bpy.context.scene.render.resolution_x = 3840
            bpy.context.scene.render.resolution_y = 2160
            bpy.context.scene.render.resolution_percentage = 100

            messageString += " Resolution,"

        if wm.bsetFramerate:
            bpy.context.scene.render.fps = 50

            messageString += " Framerate,"

        if wm.bsetEngine:
            bpy.context.scene.render.engine = 'BLENDER_EEVEE'

            messageString += " Render Engine,"

        if wm.bsetSamples:
            bpy.context.scene.eevee.taa_samples = 256
            bpy.context.scene.eevee.taa_render_samples = 256

        self.report({'INFO'}, messageString[:-1])

        return {'FINISHED'}


def register():
    bpy.utils.register_class(FTB_OT_DefaultRenderSettings_Op)


def unregister():
    bpy.utils.unregister_class(FTB_OT_DefaultRenderSettings_Op)
