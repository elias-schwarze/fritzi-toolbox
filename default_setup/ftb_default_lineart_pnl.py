import bpy

from bpy.types import Panel


class FTB_PT_DefaultAddLineart_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Line Art"
    bl_category = "FTB Defaults"

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.operator("object.default_add_lineart")


def register():
    bpy.utils.register_class(FTB_PT_DefaultAddLineart_Panel)


def unregister():
    bpy.utils.unregister_class(FTB_PT_DefaultAddLineart_Panel)
