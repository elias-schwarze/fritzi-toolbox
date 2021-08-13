import bpy

from bpy.types import Panel


class FTB_PT_PreviewRender_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Preview Render"
    bl_category = "FTB"
    bl_options = {"DEFAULT_CLOSED"}

    bpy.types.WindowManager.bEnableFront = bpy.props.BoolProperty()
    bpy.types.WindowManager.bEnableBack = bpy.props.BoolProperty()
    bpy.types.WindowManager.bEnableLeft = bpy.props.BoolProperty()
    bpy.types.WindowManager.bEnableRight = bpy.props.BoolProperty()
    bpy.types.WindowManager.bEnableTop = bpy.props.BoolProperty()
    bpy.types.WindowManager.bEnableBottom = bpy.props.BoolProperty()
    bpy.types.WindowManager.bEnable45FrontLeft = bpy.props.BoolProperty()
    bpy.types.WindowManager.bEnable45FrontRight = bpy.props.BoolProperty()
    bpy.types.WindowManager.bEnable45RearLeft = bpy.props.BoolProperty()
    bpy.types.WindowManager.bEnable45RearRight = bpy.props.BoolProperty()

    bpy.types.WindowManager.bRenderGrid = bpy.props.BoolProperty(default=False)

    bpy.types.WindowManager.sOutputPath = bpy.props.StringProperty(
        subtype='DIR_PATH', name="Output path")
    bpy.types.WindowManager.sFileName = bpy.props.StringProperty(
        subtype='FILE_NAME', name="File name")

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.operator("scene.set_jpg_output")

        col = layout.column()

        col.label(text="Output Directory:")
        col.prop(context.window_manager, "sOutputPath", text="")

        col.label(text="File Name:")
        col.prop(context.window_manager, "sFileName", text="")

        col = layout.column()
        col.prop(context.window_manager, "bRenderGrid", text="Render Grid")

        col = layout.column()
        col.scale_y = 1.5

        col.operator("object.preview_render")


class FTB_PT_PreviewSelector_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Preview Selection"
    bl_category = "FTB"
    bl_parent_id = "FTB_PT_PreviewRender_Panel"

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.prop(context.window_manager, "bEnableFront",
                 text="Front", toggle=True)
        row.prop(context.window_manager, "bEnableBack",
                 text="Back", toggle=True)

        row = layout.row(align=True)
        row.prop(context.window_manager, "bEnableLeft",
                 text="Left", toggle=True)
        row.prop(context.window_manager, "bEnableRight",
                 text="Right", toggle=True)

        row = layout.row(align=True)
        row.prop(context.window_manager, "bEnable45FrontLeft",
                 text="45° Front Left", toggle=True)
        row.prop(context.window_manager, "bEnable45FrontRight",
                 text="45° Front Right", toggle=True)

        row = layout.row(align=True)
        row.prop(context.window_manager, "bEnable45RearLeft",
                 text="45° Rear Left", toggle=True)
        row.prop(context.window_manager, "bEnable45RearRight",
                 text="45° Rear Right", toggle=True)

        row = layout.row(align=True)
        row.prop(context.window_manager, "bEnableTop",
                 text="Top", toggle=True)
        row.prop(context.window_manager, "bEnableBottom",
                 text="Bottom", toggle=True)


def register():
    bpy.utils.register_class(FTB_PT_PreviewRender_Panel)
    bpy.utils.register_class(FTB_PT_PreviewSelector_Panel)


def unregister():
    bpy.utils.unregister_class(FTB_PT_PreviewRender_Panel)
    bpy.utils.unregister_class(FTB_PT_PreviewSelector_Panel)
