import bpy
import os
import pickle

from bpy.app.handlers import persistent
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from ..utility_functions import ftb_logging as Log
from ..utility_functions.ftb_rendersettings import RenderSettings, RENDERSETTINGS_VERSION


@persistent
def clear_saved_render_settings(self, context) -> None:
    FTB_OT_RestoreRenderSettings.saved_render_settings = None


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
    bl_description = "Export and save the current render settings to *.frs file"

    filter_glob: bpy.props.StringProperty(
        default='*.frs',
        options={'HIDDEN'})

    def execute(self, context):
        filename, extension = os.path.splitext(self.filepath)

        _ext = ("", ".frs")[extension != ".frs"]
        try:
            pickle.dump(RenderSettings(), open(self.filepath + _ext, "wb"))
        except:
            Log.report(self, Log.Severity.ERROR, "File export error. Operation cancelled!")
            return {'CANCELLED'}

        Log.report(self, Log.Severity.INFO, f"Current render settings exported to \"{filename + extension}\"")
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
    import_sampling: bpy.props.BoolProperty(
        name="Import Sampling",
        default=True)
    import_AO: bpy.props.BoolProperty(
        name="Import Ambient Occlusion",
        default=True)
    import_SSR: bpy.props.BoolProperty(
        name="Import Screen Space Reflections",
        default=True)
    import_volumetrics: bpy.props.BoolProperty(
        name="Import Volumetrics",
        default=True)
    import_shadows: bpy.props.BoolProperty(
        name="Import Shadows",
        default=True)
    import_indirect_lightning: bpy.props.BoolProperty(
        name="Import Indirect Lightning",
        default=True)
    import_film_settings: bpy.props.BoolProperty(
        name="Import Film Settings",
        default=True)
    import_simplify_settings: bpy.props.BoolProperty(
        name="Import Simplify Settings",
        default=True)
    import_color_management_settings: bpy.props.BoolProperty(
        name="Import Color Management Settings",
        default=True)

    def execute(self, context):
        filename, extension = os.path.splitext(self.filepath)

        try:
            render_settings: RenderSettings = pickle.load(open(self.filepath, "rb"))
        except:
            Log.report(self, Log.Severity.ERROR, "File Import Error. Operation cancelled!")
            return {'CANCELLED'}

        if render_settings.version != RENDERSETTINGS_VERSION:
            Log.report(self, Log.Severity.WARNING,
                       "The imported file was saved with an older version of FTB. Operation cancelled!")
            return {'CANCELLED'}

        FTB_OT_RestoreRenderSettings.saved_render_settings = RenderSettings()

        Log.console(self, Log.Severity.INFO, f"Loading settings from \"{self.filepath}\":")
        if self.import_sampling:
            render_settings.eevee_sampling.load()
        if self.import_AO:
            render_settings.eevee_AO.load()
        if self.import_SSR:
            render_settings.eevee_SSR.load()
        if self.import_volumetrics:
            render_settings.eevee_volumetrics.load()
        if self.import_shadows:
            render_settings.eevee_shadows.load()
        if self.import_indirect_lightning:
            render_settings.eevee_indirect_lightning.load()
        if self.import_film_settings:
            render_settings.film.load()
        if self.import_simplify_settings:
            render_settings.simplify.load()
        if self.import_color_management_settings:
            render_settings.color_management.load()

        Log.console(self, Log.Severity.INFO, "Finished loading settings")
        Log.report(self, Log.Severity.INFO, f"Render settings imported from {filename + extension}")
        return {'FINISHED'}


class FTB_OT_RestoreRenderSettings(Operator):
    bl_idname = "scene.ftb_restore_render_settings"
    bl_label = "Restore Render Settings"
    bl_description = "Restores previous render settings before the last import"
    bl_options = {'UNDO'}

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
        return cls.saved_render_settings != None

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


classes = (FTB_OT_DefaultRenderSettings_Op, FTB_OT_ExportRenderSettings, FTB_OT_ImportRenderSettings,
           FTB_OT_RestoreRenderSettings)


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.app.handlers.load_pre.append(clear_saved_render_settings)


def unregister():
    bpy.app.handlers.load_pre.remove(clear_saved_render_settings)
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
