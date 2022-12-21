import bpy
import re

from bpy.types import Operator


class FTB_OT_SetupBurnins_Op(Operator):
    bl_idname = "object.setup_burnins"
    bl_label = "Set Burn Ins"
    bl_description = "Automatically set render burn in settings to include all required parameters"
    bl_options = {"REGISTER", "UNDO"}

    def sanitizeInput(self, context):
        """Sanitizes Input by removing letters and special characters,
        also adjusts amounts of digits to two, adds left padding with zeros if input is only one digit"""

        # First, handle case sVersionNumber is None or empty string
        if (not context.window_manager.sVersionNumber or context.window_manager.sVersionNumber == ""):
            return None

        elif (not str(context.window_manager.sVersionNumber).isdecimal()):
            # Use regex to remove non numeric characters from sVersionNumber
            context.window_manager.sVersionNumber = re.sub(
                '[^0-9]', '', context.window_manager.sVersionNumber)

    bpy.types.WindowManager.sVersionNumber = bpy.props.StringProperty(
        default="", update=sanitizeInput, name="Version Number", maxlen=2)

    def execute(self, context):

        render = bpy.context.scene.render

        render.metadata_input = 'SCENE'
        render.use_stamp_date = True
        render.use_stamp_frame = True
        render.use_stamp_filename = True
        render.use_stamp_note = True

        render.use_stamp_time = False
        render.use_stamp_render_time = False
        render.use_stamp_frame_range = False
        render.use_stamp_camera = False
        render.use_stamp_scene = False

        render.use_stamp = True
        render.stamp_font_size = 16

        singleDigits = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")

        if (context.window_manager.sVersionNumber in singleDigits):
            render.stamp_note_text = "v0" + context.window_manager.sVersionNumber

        else:
            render.stamp_note_text = "v" + context.window_manager.sVersionNumber

        self.report({'INFO'}, "Burn in set to " + render.stamp_note_text)

        return {'FINISHED'}


class FTB_OT_DisableBurnins_Op(Operator):
    bl_idname = "object.disable_burnins"
    bl_label = "Disable Burn Ins"
    bl_description = "Disable burn ins, so that they are no longer visible on the rendered image"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        bpy.context.scene.render.use_stamp = False
        self.report({'INFO'}, "Burn in disabled")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(FTB_OT_SetupBurnins_Op)
    bpy.utils.register_class(FTB_OT_DisableBurnins_Op)


def unregister():
    bpy.utils.unregister_class(FTB_OT_DisableBurnins_Op)
    bpy.utils.unregister_class(FTB_OT_SetupBurnins_Op)
