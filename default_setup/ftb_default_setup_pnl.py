import bpy

from bpy.types import Panel


class FTB_PT_Defaults_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Defaults"
    bl_category = "FTB"
    bl_options = {"DEFAULT_CLOSED"}

    bpy.types.WindowManager.bsetShadows = bpy.props.BoolProperty(default=True)

    bpy.types.WindowManager.bsetResolution = bpy.props.BoolProperty(default=True)

    bpy.types.WindowManager.bsetFramerate = bpy.props.BoolProperty(default=True)

    bpy.types.WindowManager.bsetEngine = bpy.props.BoolProperty(default=True)

    bpy.types.WindowManager.bsetSamples = bpy.props.BoolProperty(default=True)

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.label(text="Add Displacement:")

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

        col = layout.column()
        col = layout.label(text="Line Art")

        col = layout.column()
        col.operator("object.default_add_lineart")

        col = layout.column()
        col = layout.label(text="Render Settings")

        col = layout.column()
        col.operator("scene.default_render_settings")

        col = layout.column()
        col.prop(context.window_manager, "bsetSamples", text="Sample Count")

        col.prop(context.window_manager,
                 "bsetShadows", text="Shadows")

        col.prop(context.window_manager,
                 "bsetResolution", text="Resolution")

        col.prop(context.window_manager,
                 "bsetFramerate", text="Framerate")

        col.prop(context.window_manager,
                 "bsetEngine", text="Render Engine")


def register():
    bpy.utils.register_class(FTB_PT_Defaults_Panel)


def unregister():
    bpy.utils.unregister_class(FTB_PT_Defaults_Panel)
