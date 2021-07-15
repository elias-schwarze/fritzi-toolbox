import bpy
import bpy.utils
from bpy.types import Panel


class FTB_PT_DataEditing_Panel(Panel):
    bl_label = "Data Editing"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FTB"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        col = layout.column()

        col.label(text="Version Number:")

        split = layout.split(factor=0.05)
        split.label(text="v")
        split.prop(context.window_manager, "sVersionNumber", text="")

        col = layout.column()
        col.operator("object.setup_burnins")

        col = layout.column()
        col.operator("object.disable_burnins")


class FTB_PT_DataEditingDanger_Panel(Panel):
    bl_label = "Danger Zone"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FTB"
    bl_parent_id = "FTB_PT_DataEditing_Panel"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.operator("object.override_retain_transform")

        col = layout.column(align=True)
        col.operator("object.remove_all_materials",
                     text="Remove All Materials")
        col.operator("data.purge_unused", text="Purge Data")


def register():
    bpy.utils.register_class(FTB_PT_DataEditing_Panel)
    bpy.utils.register_class(FTB_PT_DataEditingDanger_Panel)


def unregister():
    bpy.utils.unregister_class(FTB_PT_DataEditingDanger_Panel)
    bpy.utils.unregister_class(FTB_PT_DataEditing_Panel)
