import bpy
from bpy.types import Panel


class FTB_PT_DefaultRenderSettings_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Render Settings"
    bl_category = "FTB Defaults"

    bpy.types.WindowManager.bsetShadows = bpy.props.BoolProperty(
        default=True)

    bpy.types.WindowManager.bsetResolution = bpy.props.BoolProperty(
        default=True)

    bpy.types.WindowManager.bsetFramerate = bpy.props.BoolProperty(
        default=True)

    bpy.types.WindowManager.bsetEngine = bpy.props.BoolProperty(
        default=True)

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.operator("scene.default_render_settings")

        col = layout.column()

        col.prop(context.window_manager,
                 "bsetShadows", text="Shadows")

        col.prop(context.window_manager,
                 "bsetResolution", text="Resolution")

        col.prop(context.window_manager,
                 "bsetFramerate", text="Framerate")

        col.prop(context.window_manager,
                 "bsetEngine", text="Render Engine")


def register():
    bpy.utils.register_class(FTB_PT_DefaultRenderSettings_Panel)


def unregister():
    bpy.utils.unregister_class(FTB_PT_DefaultRenderSettings_Panel)
