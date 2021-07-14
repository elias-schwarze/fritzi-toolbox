import bpy
import bpy.utils

from bpy.types import Panel


class FTB_PT_PreviewImport_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Preview Import"
    bl_category = "FTB"
    bl_options = {"DEFAULT_CLOSED"}

    # bpy.types.WindowManager.sLoadDirpath = bpy.props.StringProperty(
    #    subtype='DIR_PATH', name="")

    def draw(self, context):
        layout = self.layout

        #col = layout.column()
        #col.prop(context.window_manager, "sLoadDirpath")
        col = layout.column()
        col.scale_y = 1.5
        col.operator("object.preview_import")


def register():
    bpy.utils.register_class(FTB_PT_PreviewImport_Panel)


def unregister():
    bpy.utils.unregister_class(FTB_PT_PreviewImport_Panel)
