import bpy
from bpy.types import Panel


class FTB_PT_DefaultCompSetup_Panel(Panel):
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_label = "Comp Setup"
    bl_category = "FTB"

    def draw(self, context):

        layout = self.layout
        col = layout.column()
        col.operator("scene.default_comp_setup")


def register():
    bpy.utils.register_class(FTB_PT_DefaultCompSetup_Panel)


def unregister():
    bpy.utils.unregister_class(FTB_PT_DefaultCompSetup_Panel)
