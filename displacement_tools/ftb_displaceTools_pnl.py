import bpy

from bpy.types import Panel


class FTB_PT_DisplaceTools_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Displacement"
    bl_category = "FTB"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.label(text="Add Modifier:")

        col = layout.column()
        col.operator("object.add_displace_modifier",
                     text="Displace XYZ").direction = 'XYZ'

        col = layout.column(align=True)
        col.operator("object.add_displace_modifier",
                     text="Displace X").direction = 'X'

        col.operator("object.add_displace_modifier",
                     text="Displace Y").direction = 'Y'

        col.operator("object.add_displace_modifier",
                     text="Displace Z").direction = 'Z'


def register():
    bpy.utils.register_class(FTB_PT_DisplaceTools_Panel)


def unregister():
    bpy.utils.unregister_class(FTB_PT_DisplaceTools_Panel)
