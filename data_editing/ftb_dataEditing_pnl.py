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
        col.operator("object.override_retain_transform")

        col = layout.column(align=True)
        col.operator("object.remove_all_materials",
                     text="Remove All Materials")
        col.operator("data.purge_unused", text="Purge Data", icon='ERROR')


def register():
    bpy.utils.register_class(FTB_PT_DataEditing_Panel)


def unregister():
    bpy.utils.unregister_class(FTB_PT_DataEditing_Panel)
