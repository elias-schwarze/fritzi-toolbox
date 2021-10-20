import bpy
from bpy.types import Operator


class FTB_OT_batchFbxBvh_Op(Operator):
    bl_idname = "object.batch_fbx_bvh"
    bl_label = "Batch export"
    bl_description = "Batch process all selected "
    bl_options = {"REGISTER", "UNDO"}

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

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        # #bpy.ops.import_scene.fbx()
        return {'FINISHED'}


def register():
    bpy.utils.register_class(FTB_OT_batchFbxBvh_Op)


def unregister():
    bpy.utils.unregister_class(FTB_OT_batchFbxBvh_Op)
