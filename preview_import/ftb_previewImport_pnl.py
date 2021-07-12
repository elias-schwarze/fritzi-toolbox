import bpy.utils

from bpy.types import Panel


class FTB_PT_PreviewImport_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Preview Import"
    bl_category = "FTB"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        col = layout.column()


def register():
    bpy.utils.register_class(FTB_PT_PreviewImport_Panel)


def unregister():
    bpy.utils.unregister_class(FTB_PT_PreviewImport_Panel)
