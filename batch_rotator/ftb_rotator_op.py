import bpy

from bpy.types import Operator

from ..utility_functions.ftb_transform_utils import ftb_random_rotation


class FTB_OT_Random_Rotation_Op(Operator):
    bl_idname = "object.random_rotation"
    bl_label = "Randomize Rotation"
    bl_description = "Randomize rotation of selected Objects"
    bl_options = {"REGISTER", "UNDO"}

    # should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = bpy.context.object

        if obj:
            if obj.mode == "OBJECT":
                return True

        return False

    def execute(self, context):

        wm = bpy.context.window_manager

        for obj in bpy.context.selected_objects:

            if (wm.bAxisToggleX):
                obj.rotation_euler[0] += ftb_random_rotation(
                    wm.fMinRotation, wm.fMaxRotation, wm.bRandomizeDirection)

            if (wm.bAxisToggleY):
                obj.rotation_euler[1] += ftb_random_rotation(
                    wm.fMinRotation, wm.fMaxRotation, wm.bRandomizeDirection)

            if (wm.bAxisToggleZ):
                obj.rotation_euler[2] += ftb_random_rotation(
                    wm.fMinRotation, wm.fMaxRotation, wm.bRandomizeDirection)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(FTB_OT_Random_Rotation_Op)


def unregister():
    bpy.utils.unregister_class(FTB_OT_Random_Rotation_Op)
