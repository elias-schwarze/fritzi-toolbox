import bpy

# Updater ops import, all setup in this file.
from . import addon_updater_ops

from .utility_functions.ftb_path_utils import getFritziPreferences
from .default_setup.ftb_default_lineart_op import get_data_by_type_and_name, IH_MATERIAL_NAME


class FTBPreferences(bpy.types.AddonPreferences):
    """FTB preferences"""
    bl_idname = __package__

    skip_override_cleanup: bpy.props.BoolProperty(
        name="Skip Index Override Cleanup (not recommended)",
        description="If enabled, the addon will not automatically remove overrides of active_material_index (not recommended)",
        default=False)

    hide_fritzi_shader_warning: bpy.props.BoolProperty(
        name="Hide Missing Prop Shader Warning",
        description="If enabled, the Warning about missing Fritzi shaders will not be displayed in the Material Panel",
        default=False)

    alert_autokey: bpy.props.BoolProperty(
        name="Alert when Auto Keying is active (Popup message after loading blend file)",
        description="If enabled, a popup dialog is shown every time a blend file with enabled auto keying is loaded",
        default=False)

    always_disable_autokey: bpy.props.BoolProperty(
        name="Always turn off Auto Keying when loading a blend file",
        description="If enabled, auto keying will always be disabled upon loading a blend file",
        default=False)

    alert_absolute_paths: bpy.props.BoolProperty(
        name="Absolute path alert for assets",
        description="If enabled, a popup dialog is shown while saving when the file contains assets with an absolute path." +
                    " Only alerts on files saved within Fritzi Workspace",
        default=True)

    alert_auto_pack_resources: bpy.props.BoolProperty(
        name="Alert on \"Automatically Pack Resources\"",
        description=("If enabled, a popup dialog is shown every time a blend file with \"Automatically Pack Resources\""
                     "is loaded"),
        default=True)

    alert_override_auto_resync: bpy.props.BoolProperty(
        name="Alert on inactive \"Override Auto Resync\"",
        description=(
            "If enabled, a popup dialog is shown every time a blend file is loaded while \"Override Auto Resync\""
            "is disabled"),
        default=True)

    hide_render_preset_manager: bpy.props.BoolProperty(
        name="Hide Render Preset Manager",
        description="Hides the render preset manager inside the render properties tab",
        default=False)

    # Addon updater preferences.

    auto_check_update: bpy.props.BoolProperty(
        name="Auto-check for Update",
        description="If enabled, auto-check for updates using an interval",
        default=False)

    updater_interval_months: bpy.props.IntProperty(
        name='Months',
        description="Number of months between checking for updates",
        default=0,
        min=0)

    updater_interval_days: bpy.props.IntProperty(
        name='Days',
        description="Number of days between checking for updates",
        default=7,
        min=0,
        max=31)

    updater_interval_hours: bpy.props.IntProperty(
        name='Hours',
        description="Number of hours between checking for updates",
        default=0,
        min=0,
        max=23)

    updater_interval_minutes: bpy.props.IntProperty(
        name='Minutes',
        description="Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59)

    def update_ih_material_settings(self, context):
        ih_material: bpy.types.Material = get_data_by_type_and_name(bpy.types.Material, IH_MATERIAL_NAME)
        if ih_material:
            ih_material.diffuse_color = self.ih_material_diffuse_color
            ih_material.roughness = self.ih_material_roughness
            ih_material.metallic = self.ih_material_metallic

    # inverted hull settings
    ih_material_diffuse_color: bpy.props.FloatVectorProperty(name="Viewport Color",
                                                             description="",
                                                             subtype='COLOR',
                                                             size=4,
                                                             min=0.0,
                                                             max=1.0,
                                                             default=(0, 0, 0, 1),
                                                             update=update_ih_material_settings)

    ih_material_metallic: bpy.props.FloatProperty(name="Metallic",
                                                  description="",
                                                  min=0.0,
                                                  max=1.0,
                                                  default=1.0,
                                                  update=update_ih_material_settings)

    ih_material_roughness: bpy.props.FloatProperty(name="Roughness",
                                                   description="",
                                                   min=0.0,
                                                   max=1.0,
                                                   default=1.0,
                                                   update=update_ih_material_settings)

    ih_modifier_thickness: bpy.props.FloatProperty(name="Thickness",
                                                   description="",
                                                   precision=4,
                                                   default=0.0018)

    ih_modifier_offset: bpy.props.FloatProperty(name="Offset",
                                                description="",
                                                min=-1.0,
                                                max=1.0,
                                                precision=4,
                                                default=1.0)

    ih_modifier_thickness_clamp: bpy.props.FloatProperty(name="Thickness Clamp",
                                                         description="",
                                                         min=0.0,
                                                         max=2.0,
                                                         precision=4,
                                                         default=1.25)

    ih_modifier_even_thickness: bpy.props.BoolProperty(name="Even Thickness",
                                                       description="",
                                                       default=True)

    ih_modifier_use_rim: bpy.props.BoolProperty(name="Rim Fill",
                                                description="",
                                                default=True)

    ih_modifier_use_rim_only: bpy.props.BoolProperty(name="Only Rim",
                                                     description="",
                                                     default=False)

    ih_modifier_use_quality_normals: bpy.props.BoolProperty(name="High Quality Normals",
                                                            description="",
                                                            default=True)

    def draw(self, context):
        layout = self.layout

        # Works best if a column, or even just self.layout.
        mainrow = layout.row()
        col = mainrow.column()

        col.prop(getFritziPreferences(), "skip_override_cleanup")

        col.prop(getFritziPreferences(), "hide_fritzi_shader_warning")

        col.prop(getFritziPreferences(), "always_disable_autokey")

        row = col.row()
        row.prop(getFritziPreferences(), "alert_autokey")

        if (getFritziPreferences().always_disable_autokey is False):
            row.enabled = True
        else:
            row.enabled = False

        col.prop(getFritziPreferences(), "alert_auto_pack_resources")

        col.prop(getFritziPreferences(), "alert_absolute_paths")
        col.prop(getFritziPreferences(), "alert_override_auto_resync")
        col.prop(getFritziPreferences(), "hide_render_preset_manager")

        # Updater draw function, could also pass in col as third arg.
        addon_updater_ops.update_settings_ui(self, context)

        # Alternate draw function, which is more condensed and can be
        # placed within an existing draw function. Only contains:
        #   1) check for update/update now buttons
        #   2) toggle for auto-check (interval will be equal to what is set above)
        # addon_updater_ops.update_settings_ui_condensed(self, context, col)

        # Adding another column to help show the above condensed ui as one column
        # col = mainrow.column()
        # col.scale_y = 2
        # ops = col.operator("wm.url_open","Open webpage ")
        # ops.url=addon_updater_ops.updater.website


def register():
    bpy.utils.register_class(FTBPreferences)


def unregister():
    bpy.utils.unregister_class(FTBPreferences)
