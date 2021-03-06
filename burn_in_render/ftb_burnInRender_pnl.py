import bpy
import bpy.utils
from bpy.types import Panel


class FTB_PT_BurnInRender_Panel(Panel):
    bl_label = "Burn In Render"
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


def register():
    bpy.utils.register_class(FTB_PT_BurnInRender_Panel)


def unregister():
    bpy.utils.unregister_class(FTB_PT_BurnInRender_Panel)
