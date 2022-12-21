# This module handles alerts to inform the user of various issues with the file relevant to the project

import bpy
from bpy.app.handlers import persistent
from ..utility_functions.ftb_path_utils import getFritziPreferences
from ..utility_functions.ftb_string_utils import asset_path_is_absolute, file_is_in_workspace


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
    bl_options = {'INTERNAL'}

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        self.report({'INFO'}, "Auto Keying is enabled for this file")
        return context.window_manager.invoke_props_dialog(self, width=200)


class FTB_OT_Alert_Absolute_Asset_Path_Op(bpy.types.Operator):

    bl_idname = "utils.alert_absolute_asset_path"
    bl_label = "ABSOLUTE PATH ALERT"
    bl_description = "Alerts user if blend file contains absolute paths." + \
        "Only alerts on files within fritzi workspace"
    bl_options = {'INTERNAL'}

    def invoke(self, context, event):
        self.report({'WARNING'}, "\033[93m \033[1m Absolute paths found." +
                    "Check detailed item list below: \033[0m")
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.alert = True
        col.label(text="Absolute Paths Found!")
        col.alert = False
        col.label(text="File contains assets with absolute paths. Check terminal for detailed list.")
        col.label(text="Please resolve absolute to relative paths.")

    def execute(self, context):
        return {'FINISHED'}


@persistent
def auto_key_postLoad_handler(dummy):
    if (getFritziPreferences().always_disable_autokey):
        disableAutoKey()

    if (getFritziPreferences().alert_autokey and getFritziPreferences().always_disable_autokey is False):
        alertUserAutoKey()

    return {'FINISHED'}


@persistent
def custom_pre_save_handler(dummy):
    alert_on_absolute_paths = getFritziPreferences().alert_absolute_paths

    # only alert if file is within fritzi workspace and alerts are enabled
    if alert_on_absolute_paths and file_is_in_workspace():

        abs_path_errors: str = list()
        for img in bpy.data.images:
            # ignore linked + packed images
            if img.library is not None or img.packed_file is not None:
                continue

            if asset_path_is_absolute(img.filepath):
                abs_path_errors.append("\t Image \"" + img.name_full + "\" with absolute path:  " +
                                       img.filepath[:15] + "...")

        for library in bpy.data.libraries:
            # ignore indirect libraries
            if library.is_library_indirect:
                continue

            if asset_path_is_absolute(library.filepath):
                abs_path_errors.append("\t Library \"" + library.name_full + "\" with absolute path:  " +
                                       library.filepath[:15] + "...")

        if abs_path_errors:
            bpy.ops.utils.alert_absolute_asset_path('INVOKE_DEFAULT')
            for error in abs_path_errors:
                print(error)
            print("\033[96m \033[1m End of Absolute Paths List. \033[0m")

    return {'FINISHED'}


def register():
    bpy.utils.register_class(FTB_OT_AlertUserAutoKey_Op)
    bpy.utils.register_class(FTB_OT_Alert_Absolute_Asset_Path_Op)
    bpy.app.handlers.load_post.append(auto_key_postLoad_handler)
    bpy.app.handlers.save_pre.append(custom_pre_save_handler)


def unregister():
    bpy.app.handlers.save_pre.remove(custom_pre_save_handler)
    bpy.app.handlers.load_post.remove(auto_key_postLoad_handler)
    bpy.utils.unregister_class(FTB_OT_Alert_Absolute_Asset_Path_Op)
    bpy.utils.unregister_class(FTB_OT_AlertUserAutoKey_Op)
