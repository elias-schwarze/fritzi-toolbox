import bpy

from bpy.types import Panel, Menu
from ..ftb_prefs import FTBPreferences
from ..utility_functions.ftb_path_utils import getFritziPreferences


class FTB_PT_Defaults_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Defaults"
    bl_category = "FTB"
    bl_options = {"DEFAULT_CLOSED"}

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


class FTB_PT_Interval_Baking_Panel(Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = "Material Helper"
    bl_category = "FTB"
    bl_context = 'modifier'
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.operator("object.bake_interval")


def custom_object_context_menu(self, context):
    self.layout.separator()
    self.layout.operator("object.add_ih_outline")
    self.layout.operator("object.remove_ih_outline")
    self.layout.operator("object.adjust_ih_thickness")
    self.layout.separator()
    self.layout.operator("object.add_transparent_aov")
    self.layout.operator("object.remove_transparent_aov")


class FTB_PT_InvertedHullSettings_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "FTB_PT_Defaults_Panel"
    bl_label = "Inverted Hull Default Settings"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        preferences: FTBPreferences = getFritziPreferences()

        layout = self.layout
        row = layout.row()
        row.prop(preferences, "ih_material_diffuse_color")

        col = layout.column(align=False)
        col.prop(preferences, "ih_material_metallic")
        col.prop(preferences, "ih_material_roughness")

        col.separator()
        col.label(text="Solidify Settings")
        modifier_properties = ("ih_modifier_thickness", "ih_modifier_offset", "ih_modifier_even_thickness",
                               "ih_modifier_use_rim", "ih_modifier_use_rim_only", "ih_modifier_use_quality_normals",
                               "ih_modifier_thickness_clamp")
        [col.prop(preferences, property) for property in modifier_properties]


classes = (FTB_PT_Defaults_Panel, FTB_PT_RenderPresets_Panel, FTB_MT_RenderPresets_Options,
           FTB_PT_Interval_Baking_Panel, FTB_PT_InvertedHullSettings_Panel)


def append_to_outliner_context_menu(self, context):
    self.layout.operator_context = 'INVOKE_DEFAULT'
    self.layout.operator("collection.outline_character_setup")


def append_to_node_editor_context_menu(self, context):
    if context.space_data.tree_type != "ShaderNodeTree":
        return
    self.layout.separator()
    self.layout.operator_context = 'INVOKE_DEFAULT'
    self.layout.operator("node.add_transparent_aov")


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.OUTLINER_MT_object.append(draw_lineart_copy)
    bpy.types.OUTLINER_MT_object.append(custom_object_context_menu)
    bpy.types.OUTLINER_MT_collection.append(append_to_outliner_context_menu)
    bpy.types.VIEW3D_MT_object_context_menu.append(custom_object_context_menu)
    bpy.types.NODE_MT_context_menu.append(append_to_node_editor_context_menu)


def unregister():
    bpy.types.NODE_MT_context_menu.remove(append_to_node_editor_context_menu)
    bpy.types.VIEW3D_MT_object_context_menu.remove(custom_object_context_menu)
    bpy.types.OUTLINER_MT_collection.remove(append_to_outliner_context_menu)
    bpy.types.OUTLINER_MT_object.remove(custom_object_context_menu)
    bpy.types.OUTLINER_MT_object.remove(draw_lineart_copy)
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
