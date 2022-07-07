import bpy

# Updater ops import, all setup in this file.
from . import addon_updater_ops

from .utility_functions import ftb_path_utils


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

    def draw(self, context):
        layout = self.layout

        # Works best if a column, or even just self.layout.
        mainrow = layout.row()
        col = mainrow.column()

        col.prop(ftb_path_utils.getFritziPreferences(), "skip_override_cleanup")

        col.prop(ftb_path_utils.getFritziPreferences(), "hide_fritzi_shader_warning")

        col.prop(ftb_path_utils.getFritziPreferences(), "alert_autokey")

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
