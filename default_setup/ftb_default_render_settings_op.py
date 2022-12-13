import bpy
import os
import pickle
import string

from bpy.app.handlers import persistent
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from ..utility_functions import ftb_logging as Log
from ..utility_functions.ftb_rendersettings import RenderSettings, RENDERSETTINGS_VERSION


@persistent
def clear_saved_render_settings(self, context) -> None:
    FTB_OT_RestoreRenderSettings.saved_render_settings = None
    RenderPresets.load_from_disk()


class RenderPresets(bpy.types.PropertyGroup):
    presets: dict = {"None": ""}

    directory_path: str = f"{bpy.utils.resource_path('USER')}{os.sep}presets"

    @classmethod
    def load_from_disk(self):
        if not os.path.exists(self.directory_path):
            return

        self.presets.clear()
        self.presets.update({"None": ""})

        for file in os.listdir(self.directory_path):
            if not file.endswith(".frs"):
                continue

            try:
                _rs: RenderSettings = pickle.load(open(f"{self.directory_path}{os.sep}{file}", "rb"))
            except:
                Log.console(self, Log.Severity.ERROR, f"Could not import render preset \"{file}\"")
                continue

            self.presets.update({_rs.name: _rs})

    @classmethod
    def get_file_path(self, filename: str) -> str:
        return f"{self.directory_path}{os.sep}{filename}.frs"

    def item_callback(self, context):
        return [(key, key, "") for key in self.presets]

    def load_preset(self, context):
        _key = self.presets_dropdown
        if _key == "None":
            return
        Log.console(self, Log.Severity.INFO, f" Loading preset \"{_key}\"")
        self.presets[_key].load_eevee_settings()
        Log.console(self, Log.Severity.INFO, f"Preset \"{_key}\" finsihed loading")

    presets_dropdown: bpy.props.EnumProperty(
        items=item_callback,
        name="Available Presets",
        default=None,
        description="Pick a preset to load its settings.\n\nActive Preset",
        update=load_preset
    )


class FTB_OT_DefaultRenderSettings_Op(Operator):
    bl_idname = "scene.default_render_settings"
    bl_label = "Set Default Settings"
    bl_description = "Set render settings to project defaults"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        wm = bpy.context.window_manager
        if any([wm.bsetShadows, wm.bsetResolution, wm.bsetFramerate, wm.bsetEngine]):
            return True
        else:
            return False

    def execute(self, context):
        wm = bpy.context.window_manager
        messageString = "Setup successful for:"

        if wm.bsetShadows:
            bpy.context.scene.eevee.shadow_cascade_size = '4096'
            bpy.context.scene.eevee.shadow_cube_size = '4096'
            bpy.context.scene.eevee.use_shadow_high_bitdepth = True
            bpy.context.scene.eevee.use_soft_shadows = True

            # Ambient Occlusion Settings

            bpy.context.scene.eevee.use_gtao = True
            bpy.context.scene.eevee.gtao_distance = 0.5
            bpy.context.scene.eevee.gtao_factor = 1
            bpy.context.scene.eevee.gtao_quality = 1
            bpy.context.scene.eevee.use_gtao_bent_normals = True
            bpy.context.scene.eevee.use_gtao_bounce = True

            # Overscan to avoid AO fading at screen edge

            bpy.context.scene.eevee.use_overscan = True
            bpy.context.scene.eevee.overscan_size = 5

            messageString += " Shadows, Ambient Occlusion,"

        # set resolution to UHD at 100% scale

        if wm.bsetResolution:
            bpy.context.scene.render.resolution_x = 3840
            bpy.context.scene.render.resolution_y = 2160
            bpy.context.scene.render.resolution_percentage = 100

            messageString += " Resolution,"

        if wm.bsetFramerate:
            bpy.context.scene.render.fps = 50

            messageString += " Framerate,"

        if wm.bsetEngine:
            bpy.context.scene.render.engine = 'BLENDER_EEVEE'

            messageString += " Render Engine,"

        if wm.bsetSamples:
            bpy.context.scene.eevee.taa_samples = 256
            bpy.context.scene.eevee.taa_render_samples = 256

        # print string to blender output and remove last character, which is always a comma

        self.report({'INFO'}, messageString[:-1])

        return {'FINISHED'}


class FTB_OT_ExportRenderSettings(Operator, ImportHelper):
    bl_idname = "scene.ftb_export_render_settings"
    bl_label = "Export Render Settings"
    bl_description = "Export and save the current render settings preset to *.frs file"
    bl_options = {"REGISTER", "INTERNAL"}

    filter_glob: bpy.props.StringProperty(
        default='*.frs',
        options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return context.scene.ftb_render_settings.presets_dropdown != "None"

    def execute(self, context):
        filename, extension = os.path.splitext(self.filepath)

        _ext = ("", ".frs")[extension != ".frs"]
        try:
            _key = context.scene.ftb_render_settings.presets_dropdown
            pickle.dump(RenderPresets.presets[_key], open(self.filepath + _ext, "wb"))
        except:
            Log.report(self, Log.Severity.ERROR, "File export error. Operation cancelled!")
            return {'CANCELLED'}

        Log.report(self, Log.Severity.INFO, f"Current render preset exported to \"{filename + extension}\"")
        return {'FINISHED'}


class FTB_OT_ImportRenderSettings(Operator, ImportHelper):
    bl_idname = "scene.ftb_import_render_settings"
    bl_label = "Import Render Settings"
    bl_description = "Import render settings by opening a *.frs file"
    bl_options = {"REGISTER", "UNDO"}

    filter_glob: bpy.props.StringProperty(
        default='*.frs',
        options={'HIDDEN'}
    )

    def execute(self, context):
        filename, extension = os.path.splitext(self.filepath)

        try:
            render_settings: RenderSettings = pickle.load(open(self.filepath, "rb"))
        except:
            Log.report(self, Log.Severity.ERROR, "File Import Error. Operation cancelled!")
            return {'CANCELLED'}

        if render_settings.version != RENDERSETTINGS_VERSION:
            Log.report(self, Log.Severity.WARNING, "File was saved with an older version of FTB. Operation cancelled!")
            return {'CANCELLED'}

        FTB_OT_RestoreRenderSettings.saved_render_settings = RenderSettings()

        Log.console(self, Log.Severity.INFO, f"Loading settings from \"{self.filepath}\":")
        render_settings.load_eevee_settings()
        Log.console(self, Log.Severity.INFO, "Finished loading settings")

        Log.report(self, Log.Severity.INFO, f"Render settings imported from {filename + extension}")
        return {'FINISHED'}


class FTB_OT_RestoreRenderSettings(Operator):
    # DEPRECATED Operator, Poll is set to False
    bl_idname = "scene.ftb_restore_render_settings"
    bl_label = "Restore Render Settings"
    bl_description = "Restores previous render settings before the last import"
    bl_options = {'INTERNAL'}

    saved_render_settings: RenderSettings = None

    restore_sampling: bpy.props.BoolProperty(
        name="Restore Sampling",
        default=True)
    restore_AO: bpy.props.BoolProperty(
        name="Restore Ambient Occlusion",
        default=True)
    restore_SSR: bpy.props.BoolProperty(
        name="Restore Screen Space Reflections",
        default=True)
    restore_volumetrics: bpy.props.BoolProperty(
        name="Restore Volumetrics",
        default=True)
    restore_shadows: bpy.props.BoolProperty(
        name="Restore Shadows",
        default=True)
    restore_indirect_lightning: bpy.props.BoolProperty(
        name="Restore Indirect Lightning",
        default=True)
    restore_film_settings: bpy.props.BoolProperty(
        name="Restore Film Settings",
        default=True)
    restore_simplify_settings: bpy.props.BoolProperty(
        name="Restore Simplify Settings",
        default=True)
    restore_color_management_settings: bpy.props.BoolProperty(
        name="Restore Color Management Settings",
        default=True)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=350)

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        col.prop(self, "restore_sampling")
        col.prop(self, "restore_AO")
        col.prop(self, "restore_SSR")
        col.prop(self, "restore_volumetrics")
        col.prop(self, "restore_shadows")
        col.prop(self, "restore_indirect_lightning")
        col.prop(self, "restore_film_settings")
        col.prop(self, "restore_simplify_settings")
        col.prop(self, "restore_color_management_settings")

    @classmethod
    def poll(cls, context):
        return False

    def execute(self, context):

        Log.console(self, Log.Severity.INFO, "Restoring stored settings:")
        if self.restore_sampling:
            self.saved_render_settings.eevee_sampling.load()
        if self.restore_AO:
            self.saved_render_settings.eevee_AO.load()
        if self.restore_SSR:
            self.saved_render_settings.eevee_SSR.load()
        if self.restore_volumetrics:
            self.saved_render_settings.eevee_volumetrics.load()
        if self.restore_shadows:
            self.saved_render_settings.eevee_shadows.load()
        if self.restore_indirect_lightning:
            self.saved_render_settings.eevee_indirect_lightning.load()
        if self.restore_film_settings:
            self.saved_render_settings.film.load()
        if self.restore_simplify_settings:
            self.saved_render_settings.simplify.load()
        if self.restore_color_management_settings:
            self.saved_render_settings.color_management.load()

        Log.console(self, Log.Severity.INFO, "Finished restoring settings")
        Log.report(self, Log.Severity.INFO, "Render settings restored")
        return {'FINISHED'}


class FTB_OT_AddRenderPreset(Operator):
    bl_idname = "scene.ftb_add_render_preset"
    bl_label = "Add Render Preset"
    bl_description = "Saves current render settings as a new preset"
    bl_options = {'REGISTER'}

    preset_name: bpy.props.StringProperty(
        name="Name",
        default=""
    )
    invalid_name: bpy.props.BoolProperty(
        default=False
    )
    name_duplicate: bpy.props.BoolProperty(
        default=False
    )

    def is_valid_preset_name(self, name: str) -> bool:
        _valid_chars = string.ascii_letters + string.digits + "-_"
        for c in name:
            if c not in _valid_chars:
                return False
        return name != ""

    def invoke(self, context, event):
        self.preset_name = ""
        return context.window_manager.invoke_props_dialog(self, width=350)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        if self.invalid_name:
            col.alert = True
            col.label(text="Only letters, digits, - and _ are allowed in names!")
            col.label(text="No whitespaces and Name may not be empty!")
            col.alert = False
        elif self.name_duplicate:
            col.alert = True
            col.label(text="Preset with that name already exists.")
            col.label(text="Pick another name")
            col.alert = False
        col.prop(self, "preset_name")

    def execute(self, context):

        if not os.path.exists(RenderPresets.directory_path):
            try:
                os.mkdir(RenderPresets.directory_path)
            except RuntimeError as err:
                Log.report(self, Log.Severity.ERROR, f"{err} - Could not create presets directory")
                return {'CANCELLED'}

        self.invalid_name = not self.is_valid_preset_name(self.preset_name)
        if self.invalid_name:
            Log.console(self, Log.Severity.ERROR, f"Invalid name for preset")
            return context.window_manager.invoke_props_dialog(self, width=350)

        self.name_duplicate = self.preset_name in RenderPresets.presets
        if self.name_duplicate:
            Log.console(self, Log.Severity.ERROR, f"Preset with name \"{self.preset_name}\" already exists!")
            return context.window_manager.invoke_props_dialog(self, width=350)

        _rs = RenderSettings(self.preset_name)
        try:
            pickle.dump(_rs, open(RenderPresets.get_file_path(self.preset_name), "wb"))
        except:
            Log.console(self, Log.Severity.ERROR, f"Failed creating preset \"{self.preset_name}\".Operation cancelled!")
            return {'CANCELLED'}

        RenderPresets.presets.update({self.preset_name: _rs})
        bpy.context.scene.ftb_render_settings.presets_dropdown = self.preset_name

        Log.report(self, Log.Severity.INFO, f"New render preset \"{self.preset_name}\" added!")
        return {'FINISHED'}


class FTB_OT_EditRenderPreset(Operator):
    bl_idname = "scene.ftb_edit_render_preset"
    bl_label = "Edit Render Preset"
    bl_description = "Overrides the selected preset with the current render settings"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.scene.ftb_render_settings.presets_dropdown != "None"

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=500)

    def draw(self, context):
        layout = self.layout
        layout.label(text="This will override the current preset with the current render settings.")
        layout.label(text="Are you sure?")

    def execute(self, context):
        _key = context.scene.ftb_render_settings.presets_dropdown
        _rs = RenderSettings(_key)
        try:
            pickle.dump(_rs, open(RenderPresets.get_file_path(_key), "wb"))
        except:
            Log.console(self, Log.Severity.ERROR, f"Failed editing preset \"{_key}\".Operation cancelled!")
            return {'CANCELLED'}

        RenderPresets.presets[_key] = _rs

        Log.report(self, Log.Severity.INFO, f"Preset \"{_key}\" has been updated!")
        return {'FINISHED'}


class FTB_OT_RemoveRenderPreset(Operator):
    bl_idname = "scene.ftb_remove_render_preset"
    bl_label = "Remove Render Preset"
    bl_description = "Deletes the currently selected preset"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.scene.ftb_render_settings.presets_dropdown != "None"

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.label(text="This will delete the current preset.")
        layout.label(text="Are you sure?")

    def execute(self, context):
        _key = context.scene.ftb_render_settings.presets_dropdown
        try:
            os.remove(RenderPresets.get_file_path(_key))
        except:
            Log.report(self, Log.Severity.ERROR, f"Could not remove preset \"{_key}\"! Operation cancelled!")
            return {'CANCELLED'}

        RenderPresets.presets.pop(_key)
        context.scene.ftb_render_settings.presets_dropdown = 'None'

        Log.report(self, Log.Severity.INFO, f"Preset \"{_key}\" has been deleted!")
        return {'FINISHED'}


classes = (FTB_OT_DefaultRenderSettings_Op, FTB_OT_ExportRenderSettings, FTB_OT_ImportRenderSettings,
           FTB_OT_RestoreRenderSettings, FTB_OT_AddRenderPreset, FTB_OT_EditRenderPreset,
           FTB_OT_RemoveRenderPreset, RenderPresets)


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.ftb_render_settings = bpy.props.PointerProperty(type=RenderPresets)
    bpy.app.handlers.load_pre.append(clear_saved_render_settings)

    RenderPresets.load_from_disk()


def unregister():
    bpy.app.handlers.load_pre.remove(clear_saved_render_settings)
    del bpy.types.Scene.ftb_render_settings
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
