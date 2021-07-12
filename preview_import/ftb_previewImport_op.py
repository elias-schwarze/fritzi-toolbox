import bpy
from bpy.types import Operator


class FTB_OT_Preview_Import_Op(Operator):
    bl_idname = "object.preview_import"
    bl_label = "Import Previews"
    bl_description = "Import previews"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        return {'FINISHED'}


def register():
    bpy.utils.register_class(FTB_OT_Preview_Import_Op)


def unregister():
    bpy.utils.unregister_class(FTB_OT_Preview_Import_Op)
