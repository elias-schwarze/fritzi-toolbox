import bpy
import bpy.utils

from bpy.types import Panel


class FTB_PT_UEExport_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Unreal Export Scripts"
    bl_category = "FTB"
    bl_options = {"DEFAULT_CLOSED"}

    bpy.types.WindowManager.ftbExportRecalcNormals = bpy.props.BoolProperty(default=True, description="Recalculate normals when running this step. Disable if normals are already correct or recalculation causes errors")

    def draw(self, context):

        layout = self.layout

        col = layout.column()
        col.label(text="Step 1")
        col.operator("utils.basicprep")
        col.prop(bpy.context.window_manager, "ftbExportRecalcNormals", text="Recalculate Normals")

        col.separator()

        col.label(text="Optional Steps")
        col.operator("utils.dissolvecollections")
        col.operator("utils.materialprep")
        col.operator("utils.deletemods")
        col.operator("object.flipnormals")

        col.separator()
        col.label(text="Character Tools")
        col.operator("utils.ue_char_cleanup")
        col.operator("utils.ue_char_weight_parent")


def register():
    bpy.utils.register_class(FTB_PT_UEExport_Panel)


def unregister():
    bpy.utils.unregister_class(FTB_PT_UEExport_Panel)
