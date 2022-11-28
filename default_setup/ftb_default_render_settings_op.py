import bpy
import os
import pickle

from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from ..utility_functions.ftb_rendersettings import RenderSettings, RENDERSETTINGS_VERSION


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
    bl_idname = "scene.export_render_settings"
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
        except RuntimeError as err:
            self.report({'ERROR'}, "File export error. Operation cancelled!")
            return {'CANCELLED'}

        self.report({'INFO'}, f"Render settings exported to {filename + extension}")
        return {'FINISHED'}


class FTB_OT_ImportRenderSettings(Operator, ImportHelper):
    bl_idname = "scene.import_render_settings"
    bl_label = "Import Render Settings"
    bl_description = "Import render settings by opening a *.frs file"
    bl_options = {"REGISTER", "UNDO"}

    def load_sampling(self, settings: RenderSettings.EeveeSampling) -> None:
        eevee = bpy.context.scene.eevee
        eevee.taa_render_samples = settings.taa_render_samples
        eevee.taa_samples = settings.taa_samples
        eevee.use_taa_reprojection = settings.use_taa_reprojection

    def load_AO(self, settings: RenderSettings.EeveeAO) -> None:
        eevee = bpy.context.scene.eevee
        eevee.use_gtao = settings.use_gtao
        eevee.gtao_distance = settings.gtao_distance
        eevee.gtao_factor = settings.gtao_factor
        eevee.gtao_quality = settings.gtao_quality
        eevee.use_gtao_bent_normals = settings.use_gtao_bent_normals
        eevee.use_gtao_bounce = settings.use_gtao_bounce

    def load_SSR(self, settings: RenderSettings.EeveeSSR) -> None:
        eevee = bpy.context.scene.eevee
        eevee.use_ssr = settings.use_ssr
        eevee.use_ssr_refraction = settings.use_ssr_refraction
        eevee.use_ssr_halfres = settings.use_ssr_halfres
        eevee.ssr_quality = settings.ssr_quality
        eevee.ssr_max_roughness = settings.ssr_max_roughness
        eevee.ssr_thickness = settings.ssr_thickness
        eevee.ssr_border_fade = settings.ssr_border_fade
        eevee.ssr_firefly_fac = settings.ssr_firefly_fac

    def load_volumetrics(self, settings: RenderSettings.EeveeVolumetrics) -> None:
        eevee = bpy.context.scene.eevee
        eevee.volumetric_start = settings.volumetric_start
        eevee.volumetric_end = settings.volumetric_end
        eevee.volumetric_tile_size = settings.volumetric_tile_size
        eevee.volumetric_samples = settings.volumetric_samples
        eevee.volumetric_sample_distribution = settings.volumetric_sample_distribution
        eevee.use_volumetric_lights = settings.use_volumetric_lights
        eevee.volumetric_light_clamp = settings.volumetric_light_clamp
        eevee.use_volumetric_shadows = settings.use_volumetric_shadows
        eevee.volumetric_shadow_samples = settings.volumetric_shadow_samples

    def load_shadows(self, settings: RenderSettings.EeveeShadows) -> None:
        eevee = bpy.context.scene.eevee
        eevee.shadow_cube_size = settings.shadow_cube_size
        eevee.shadow_cascade_size = settings.shadow_cascade_size
        eevee.use_shadow_high_bitdepth = settings.use_shadow_high_bitdepth
        eevee.use_soft_shadows = settings.use_soft_shadows
        eevee.light_threshold = settings.light_threshold

    def load_indirect_lightning(self, settings: RenderSettings.EeveeIndirectLightning) -> None:
        eevee = bpy.context.scene.eevee
        eevee.gi_auto_bake = settings.gi_auto_bake
        eevee.gi_diffuse_bounces = settings.gi_diffuse_bounces
        eevee.gi_cubemap_resolution = settings.gi_cubemap_resolution
        eevee.gi_visibility_resolution = settings.gi_visibility_resolution
        eevee.gi_irradiance_smoothing = settings.gi_irradiance_smoothing
        eevee.gi_glossy_clamp = settings.gi_glossy_clamp
        eevee.gi_filter_quality = settings.gi_filter_quality
        eevee.gi_cubemap_display_size = settings.gi_cubemap_display_size
        eevee.gi_show_cubemaps = settings.gi_show_cubemaps
        eevee.gi_irradiance_display_size = settings.gi_irradiance_display_size
        eevee.gi_show_irradiance = settings.gi_show_irradiance

    def load_film_settings(self, settings: RenderSettings.Film) -> None:
        eevee = bpy.context.scene.eevee
        render = bpy.context.scene.render
        render.filter_size = settings.filter_size
        render.film_transparent = settings.film_transparent
        eevee.use_overscan = settings.overscan_size
        eevee.overscan_size = settings.overscan_size

    def load_simplify_settings(self, settings: RenderSettings.Simplify) -> None:
        render = bpy.context.scene.render
        render.use_simplify = settings.use_simplify
        render.simplify_subdivision = settings.simplify_subdivision
        render.simplify_child_particles = settings.simplify_child_particles
        render.simplify_volumes = settings.simplify_volumes
        render.simplify_subdivision_render = settings.simplify_subdivision_render
        render.simplify_child_particles_render = settings.simplify_child_particles_render
        render.simplify_gpencil = settings.simplify_gpencil
        render.simplify_gpencil_onplay = settings.simplify_gpencil_onplay
        render.simplify_gpencil_view_fill = settings.simplify_gpencil_view_fill
        render.simplify_gpencil_modifier = settings.simplify_gpencil_modifier
        render.simplify_gpencil_shader_fx = settings.simplify_gpencil_shader_fx
        render.simplify_gpencil_tint = settings.simplify_gpencil_tint
        render.simplify_gpencil_antialiasing = settings.simplify_gpencil_antialiasing

    def load_color_management_settings(self, settings: RenderSettings.ColorManagement) -> None:
        display_settings = bpy.context.scene.display_settings
        view_settings = bpy.context.scene.view_settings
        sequencer_colorspace_settings = bpy.context.scene.sequencer_colorspace_settings
        display_settings.display_device = settings.display_device
        view_settings.view_transform = settings.view_transform
        view_settings.look = settings.look
        view_settings.exposure = settings.exposure
        view_settings.gamma = settings.gamma
        sequencer_colorspace_settings.name = settings.name

    filter_glob: bpy.props.StringProperty(
        default='*.frs',
        options={'HIDDEN'}
    )
    import_sampling: bpy.props.BoolProperty(
        name="Import Sampling",
        description="",
        default=True
    )
    import_AO: bpy.props.BoolProperty(
        name="Import Ambient Occlusion",
        description="",
        default=True
    )
    import_SSR: bpy.props.BoolProperty(
        name="Import Screen Space Reflections",
        description="",
        default=True
    )
    import_volumetrics: bpy.props.BoolProperty(
        name="Import Volumetrics",
        description="",
        default=True
    )
    import_shadows: bpy.props.BoolProperty(
        name="Import Shadows",
        description="",
        default=True
    )
    import_indirect_lightning: bpy.props.BoolProperty(
        name="Import Indirect Lightning",
        description="",
        default=True
    )
    import_film_settings: bpy.props.BoolProperty(
        name="Import Film Settings",
        description="",
        default=True
    )
    import_simplify_settings: bpy.props.BoolProperty(
        name="Import Simplify Settings",
        description="",
        default=True
    )
    import_color_management_settings: bpy.props.BoolProperty(
        name="Import Color Management Settings",
        description="",
        default=True
    )

    def execute(self, context):
        # TODO:
        # render settings data structure verification
        try:
            render_settings: RenderSettings = pickle.load(open(self.filepath, "rb"))
        except:
            self.report({'ERROR'}, "File Import Error. Operation cancelled!")
            return {'CANCELLED'}

        if render_settings.version != RENDERSETTINGS_VERSION:
            self.report({'WARNING'}, "The imported file was saved with an older version of FTB. Operation cancelled!")
            return {'CANCELLED'}

        print(render_settings.data_id)
        print(render_settings.version)

        if self.import_sampling:
            self.load_sampling(render_settings.eevee_sampling)
        if self.import_AO:
            self.load_AO(render_settings.eevee_AO)
        if self.import_SSR:
            self.load_SSR(render_settings.eevee_SSR)
        if self.import_volumetrics:
            self.load_volumetrics(render_settings.eevee_volumetrics)
        if self.import_shadows:
            self.load_shadows(render_settings.eevee_shadows)
        if self.import_indirect_lightning:
            self.load_indirect_lightning(render_settings.eevee_indirect_lightning)
        if self.import_film_settings:
            self.load_film_settings(render_settings.film)
        if self.import_simplify_settings:
            self.load_simplify_settings(render_settings.simplify)
        if self.import_color_management_settings:
            self.load_color_management_settings(render_settings.color_management)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(FTB_OT_DefaultRenderSettings_Op)
    bpy.utils.register_class(FTB_OT_ExportRenderSettings)
    bpy.utils.register_class(FTB_OT_ImportRenderSettings)


def unregister():
    bpy.utils.unregister_class(FTB_OT_ImportRenderSettings)
    bpy.utils.unregister_class(FTB_OT_ExportRenderSettings)
    bpy.utils.unregister_class(FTB_OT_DefaultRenderSettings_Op)
