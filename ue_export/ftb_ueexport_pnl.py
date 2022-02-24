import bpy
import bpy.utils

from bpy.types import Panel


class FTB_PT_UEExport_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Unreal Export Scripts"
    bl_category = "FTB"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):

        layout = self.layout

        col = layout.column()
        col.label(text="Step 1")
        col.operator("utils.basicprep")
        col.label(text="Optional Steps")
        col.operator("utils.dissolvecollections")
        col.operator("utils.materialprep")
        col.operator("utils.deletemods")
        col.operator("object.flipnormals")


def register():
    bpy.utils.register_class(FTB_PT_UEExport_Panel)


def unregister():
    bpy.utils.unregister_class(FTB_PT_UEExport_Panel)
