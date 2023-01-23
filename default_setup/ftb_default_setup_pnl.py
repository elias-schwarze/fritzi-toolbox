import bpy

from bpy.types import Panel, Menu
from ..utility_functions.ftb_path_utils import getFritziPreferences


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


class FTB_PT_RenderPresets_Panel(Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = "Render Presets"
    bl_category = "FTB"
    bl_context = 'render'
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        if getFritziPreferences().hide_render_preset_manager:
            return

        layout = self.layout
        layout.use_property_decorate = False

        row = layout.row(align=True)

        row.prop(context.scene.ftb_render_settings, "presets_dropdown", text="")
        row.operator("scene.ftb_add_render_preset", text="", icon='ADD')
        row.operator("scene.ftb_edit_render_preset", text="", icon='CURRENT_FILE')
        row.operator("scene.ftb_remove_render_preset", text="", icon='REMOVE')
        row.menu(menu="FTB_MT_RenderPresets_Options", text="", icon="DOWNARROW_HLT")


def draw_lineart_copy(self, context):
    if context.selected_ids:
        if getattr(context.selected_ids[0], "type", None) == 'GPENCIL':
            layout = self.layout
            layout.separator()
            layout.operator("outliner.copy_optimize_lines")


class FTB_MT_RenderPresets_Options(Menu):
    bl_label = "Render Preset Operators"
    bl_category = "FTB"

    def draw(self, context):
        layout = self.layout
        layout.operator("scene.ftb_import_render_settings", emboss=False)
        layout.operator("scene.ftb_export_render_settings", emboss=False)


def register():
    bpy.utils.register_class(FTB_PT_Defaults_Panel)
    bpy.utils.register_class(FTB_PT_RenderPresets_Panel)
    bpy.utils.register_class(FTB_MT_RenderPresets_Options)
    bpy.types.OUTLINER_MT_object.append(draw_lineart_copy)


def unregister():
    bpy.types.OUTLINER_MT_object.remove(draw_lineart_copy)
    bpy.utils.unregister_class(FTB_MT_RenderPresets_Options)
    bpy.utils.unregister_class(FTB_PT_RenderPresets_Panel)
    bpy.utils.unregister_class(FTB_PT_Defaults_Panel)
