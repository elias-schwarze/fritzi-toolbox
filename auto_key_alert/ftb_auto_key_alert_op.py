# This module handles the dialog box that shows after loading a blend file, to inform the user that the auto keying option is currently enabled

import bpy
from bpy.app.handlers import persistent
from ..utility_functions.ftb_path_utils import getFritziPreferences


def alertUserAutoKey():
    if (bpy.context.scene.tool_settings.use_keyframe_insert_auto):
        bpy.ops.utils.alert_user_auto_key('INVOKE_DEFAULT')

def disableAutoKey():
    if (bpy.context.scene.tool_settings.use_keyframe_insert_auto):
        bpy.context.scene.tool_settings.use_keyframe_insert_auto = False
        

class FTB_OT_AlertUserAutoKey_Op(bpy.types.Operator):

    bl_idname = "utils.alert_user_auto_key"
    bl_label = "Info: Auto keying active for this file!"
    bl_description = "Alert Auto Key"

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        self.report({'INFO'}, "Auto Keying is enabled for this file")
        return context.window_manager.invoke_props_dialog(self, width=200)


@persistent
def auto_key_postLoad_handler(dummy):
    if (getFritziPreferences().always_disable_autokey):
        disableAutoKey()


    if (getFritziPreferences().alert_autokey and getFritziPreferences().always_disable_autokey == False):
        alertUserAutoKey()

    return {'FINISHED'}

def register():
    bpy.utils.register_class(FTB_OT_AlertUserAutoKey_Op)
    bpy.app.handlers.load_post.append(auto_key_postLoad_handler)

def unregister():
    bpy.app.handlers.load_post.remove(auto_key_postLoad_handler)
    bpy.utils.unregister_class(FTB_OT_AlertUserAutoKey_Op)
