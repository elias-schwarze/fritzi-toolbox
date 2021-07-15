import bpy
import re

from bpy.types import Operator

from .. utility_functions.ftb_transform_utils import ob_Copy_Vis_Loc
from .. utility_functions.ftb_transform_utils import ob_Copy_Vis_Rot
from .. utility_functions.ftb_transform_utils import ob_Copy_Vis_Sca
from .. utility_functions.ftb_string_utils import strip_End_Numbers


class FTB_OT_RemoveMaterials_Op(Operator):
    bl_idname = "object.remove_all_materials"
    bl_label = "Remove All Materials"
    bl_description = "Remove all Material slots from all selected Objects"
    bl_options = {"REGISTER", "UNDO"}

    # should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object

        if obj:
            if obj.mode == "OBJECT":
                return True

        return False

    def execute(self, context):
        for m in bpy.data.materials:
            bpy.data.materials.remove(m)

        self.report({'INFO'}, 'Removed all Materials')
        return {'FINISHED'}

    def invoke(self, context, event):
        return bpy.context.window_manager.invoke_confirm(self, event)


class FTB_OT_PurgeUnusedData_Op(Operator):
    bl_idname = "data.purge_unused"
    bl_label = "Purge Unused Data"
    bl_description = "Recursively remove all unused Datablocks from file"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.outliner.orphans_purge(
            do_local_ids=True, do_linked_ids=True, do_recursive=True)
        self.report({'INFO'}, 'Purged unused Data')
        return {'FINISHED'}

    def invoke(self, context, event):
        return bpy.context.window_manager.invoke_confirm(self, event)


class FTB_OT_OverrideRetainTransform_Op(Operator):
    bl_idname = "object.override_retain_transform"
    bl_label = "Override Keep Transform"
    bl_description = "Make a library override and retain the transform of the previous instance object"
    bl_options = {"REGISTER", "UNDO"}

    # should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object

        if obj:
            if obj.mode == "OBJECT" and obj.type == 'EMPTY' and obj.is_instancer:
                return True
        return False

    def execute(self, context):
        objName = context.active_object.name
        objLoc = context.active_object.location
        objRot = context.active_object.rotation_euler
        objScale = context.active_object.scale

        # add new empty object to temporarily store transform and parent matrix of linked object
        tempOb = bpy.data.objects.new(objName + "phx", None)
        bpy.context.scene.collection.objects.link(tempOb)

        # tempOb copy transform from linked object
        ob_Copy_Vis_Loc(tempOb, context.active_object)
        ob_Copy_Vis_Rot(tempOb, context.active_object)
        ob_Copy_Vis_Sca(tempOb, context.active_object)

        # rename the linked object before overriding, so the objects created by
        # library override can have the same name as the original linked object had
        bpy.context.active_object.name = objName + "phName"

        bpy.ops.object.make_override_library()
        newOb = bpy.data.collections[strip_End_Numbers(
            objName)].objects[strip_End_Numbers(objName)]

        ob_Copy_Vis_Loc(newOb, tempOb)
        ob_Copy_Vis_Rot(newOb, tempOb)
        ob_Copy_Vis_Sca(newOb, tempOb)

        bpy.data.objects.remove(tempOb, do_unlink=True)

        return {'FINISHED'}

    def invoke(self, context, event):
        return bpy.context.window_manager.invoke_confirm(self, event)


class FTB_OT_SetupBurnins_Op(Operator):
    bl_idname = "object.setup_burnins"
    bl_label = "Set Burn Ins"
    bl_description = "Automatically set render burn in settings to include all required parameters"
    bl_options = {"REGISTER", "UNDO"}

    def sanitizeInput(self, context):
        """Sanitizes Input by removing letters and special characters, also adjusts amounts of digits to two, adds left padding with zeros if input is only one digit"""

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

        render.image_settings.file_format = 'JPEG'
        render.image_settings.quality = 90

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
    bpy.utils.register_class(FTB_OT_RemoveMaterials_Op)
    bpy.utils.register_class(FTB_OT_PurgeUnusedData_Op)
    bpy.utils.register_class(FTB_OT_OverrideRetainTransform_Op)
    bpy.utils.register_class(FTB_OT_SetupBurnins_Op)
    bpy.utils.register_class(FTB_OT_DisableBurnins_Op)


def unregister():
    bpy.utils.unregister_class(FTB_OT_DisableBurnins_Op)
    bpy.utils.unregister_class(FTB_OT_SetupBurnins_Op)
    bpy.utils.unregister_class(FTB_OT_RemoveMaterials_Op)
    bpy.utils.unregister_class(FTB_OT_PurgeUnusedData_Op)
    bpy.utils.unregister_class(FTB_OT_OverrideRetainTransform_Op)
