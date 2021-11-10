import bpy
from bpy.types import Panel
from bpy.props import StringProperty


class FTB_PT_FbxToBvh_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "FbxToBvh"
    bl_category = "FTB"
    bl_options = {"DEFAULT_CLOSED"}

    bpy.types.WindowManager.bvhOutputPath = StringProperty(
        subtype='DIR_PATH', name="Output path")

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.label(text="Output Directory:")
        col.prop(context.window_manager, "bvhOutputPath", text="")

        col = layout.column()
        col.operator("object.batch_fbx_bvh")


def register():
    bpy.utils.register_class(FTB_PT_FbxToBvh_Panel)


def unregister():
    bpy.utils.unregister_class(FTB_PT_FbxToBvh_Panel)
