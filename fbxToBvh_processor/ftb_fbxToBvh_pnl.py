import bpy
from bpy.types import Panel


class FTB_PT_FbxToBvh_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "FbxToBvh"
    bl_category = "FTB Batching"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.operator("object.batch_fbx_bvh")


def register():
    bpy.utils.register_class(FTB_PT_FbxToBvh_Panel)


def unregister():
    bpy.utils.unregister_class(FTB_PT_FbxToBvh_Panel)
