import bpy          # keep this! its called using the eval() and exec() method inside the Settings class!

RENDERSETTINGS_VERSION = (0, 9, 5)


class RenderSettings:

    class Settings:
        full_data_paths: list[str] = []
        __settings: dict

        def __init__(self) -> None:
            self.__settings = {}
            for item in self.full_data_paths:
                try:
                    iter(item)
                    _value = (list(eval(item)), eval(item))[isinstance(eval(item), str)]
                except:
                    _value = eval(item)
                self.__settings.update({item.split(".")[-1]: _value})

        def load(self) -> None:
            print(f"\tLoading {self.__class__.__name__} Settings:")
            for item in self.full_data_paths:
                _value = self.__settings[item.split('.')[-1]]
                _value_str = (f"{_value}", f"'{_value}'")[type(eval(item)) == str]
                print(f"\t\tSetting {item.split('.')[-1]} from {eval(item)} to {_value_str}")
                exec(f"{item} = {_value_str}")

        def __str__(self) -> str:
            _str = f"\t{self.__class__.__name__}\n"
            _str += f"\t{{\n"
            for key in self.__settings:
                _str += f"\t\t{key} = {self.__settings[key]}\n"
            _str += f"\t}}\n"
            return _str

    class Performance(Settings):
        full_data_paths = ["bpy.context.scene.render.use_high_quality_normals"]

    class Curves(Settings):
        full_data_paths = ["bpy.context.scene.render.hair_type",
                           "bpy.context.scene.render.hair_subdiv"]

    class Film(Settings):
        full_data_paths = ["bpy.context.scene.render.filter_size",
                           "bpy.context.scene.render.film_transparent",
                           "bpy.context.scene.eevee.use_overscan",
                           "bpy.context.scene.eevee.overscan_size"]

    class Simplify(Settings):
        full_data_paths = ["bpy.context.scene.render.use_simplify",
                           "bpy.context.scene.render.simplify_subdivision",
                           "bpy.context.scene.render.simplify_child_particles",
                           "bpy.context.scene.render.simplify_volumes",
                           "bpy.context.scene.render.simplify_subdivision_render",
                           "bpy.context.scene.render.simplify_child_particles_render",
                           "bpy.context.scene.render.simplify_gpencil",
                           "bpy.context.scene.render.simplify_gpencil_onplay",
                           "bpy.context.scene.render.simplify_gpencil_view_fill",
                           "bpy.context.scene.render.simplify_gpencil_modifier",
                           "bpy.context.scene.render.simplify_gpencil_shader_fx",
                           "bpy.context.scene.render.simplify_gpencil_tint",
                           "bpy.context.scene.render.simplify_gpencil_antialiasing"]

    class GreasePencil(Settings):
        full_data_paths = ["bpy.context.scene.grease_pencil_settings.antialias_threshold"]

    class Freestyle(Settings):
        full_data_paths = ["bpy.context.scene.render.use_freestyle",
                           "bpy.context.scene.render.line_thickness_mode",
                           "bpy.context.scene.render.line_thickness"]

    class ColorManagement(Settings):
        full_data_paths = ["bpy.context.scene.display_settings.display_device",
                           "bpy.context.scene.view_settings.view_transform",
                           "bpy.context.scene.view_settings.look",
                           "bpy.context.scene.view_settings.exposure",
                           "bpy.context.scene.view_settings.gamma",
                           "bpy.context.scene.sequencer_colorspace_settings.name"]

    class EeveeSampling(Settings):
        full_data_paths = ["bpy.context.scene.eevee.taa_render_samples",
                           "bpy.context.scene.eevee.taa_samples",
                           "bpy.context.scene.eevee.use_taa_reprojection"]

    class EeveeBloom(Settings):
        full_data_paths = ["bpy.context.scene.eevee.use_bloom",
                           "bpy.context.scene.eevee.bloom_threshold",
                           "bpy.context.scene.eevee.bloom_knee",
                           "bpy.context.scene.eevee.bloom_radius",
                           "bpy.context.scene.eevee.bloom_color",
                           "bpy.context.scene.eevee.bloom_intensity",
                           "bpy.context.scene.eevee.bloom_clamp",
                           "bpy.context.scene.eevee.use_bloom"]

    class EeveeDOF(Settings):
        full_data_paths = ["bpy.context.scene.eevee.bokeh_max_size",
                           "bpy.context.scene.eevee.bokeh_threshold",
                           "bpy.context.scene.eevee.bokeh_neighbor_max",
                           "bpy.context.scene.eevee.bokeh_denoise_fac",
                           "bpy.context.scene.eevee.use_bokeh_high_quality_slight_defocus",
                           "bpy.context.scene.eevee.use_bokeh_jittered",
                           "bpy.context.scene.eevee.bokeh_overblur"]

    class EeveeAO(Settings):
        full_data_paths = ["bpy.context.scene.eevee.use_gtao",
                           "bpy.context.scene.eevee.gtao_distance",
                           "bpy.context.scene.eevee.gtao_factor",
                           "bpy.context.scene.eevee.gtao_quality",
                           "bpy.context.scene.eevee.use_gtao_bent_normals",
                           "bpy.context.scene.eevee.use_gtao_bounce"]

    class EeveeSSS(Settings):
        full_data_paths = ["bpy.context.scene.eevee.sss_samples",
                           "bpy.context.scene.eevee.sss_jitter_threshold"]

    class EeveeSSR(Settings):
        full_data_paths = ["bpy.context.scene.eevee.use_ssr",
                           "bpy.context.scene.eevee.use_ssr_refraction",
                           "bpy.context.scene.eevee.use_ssr_halfres",
                           "bpy.context.scene.eevee.ssr_quality",
                           "bpy.context.scene.eevee.ssr_max_roughness",
                           "bpy.context.scene.eevee.ssr_thickness",
                           "bpy.context.scene.eevee.ssr_border_fade",
                           "bpy.context.scene.eevee.ssr_firefly_fac"]

    class EeveeMotionBlur(Settings):
        full_data_paths = ["bpy.context.scene.eevee.use_motion_blur",
                           "bpy.context.scene.eevee.motion_blur_position",
                           "bpy.context.scene.eevee.motion_blur_shutter",
                           "bpy.context.scene.eevee.motion_blur_depth_scale",
                           "bpy.context.scene.eevee.motion_blur_max",
                           "bpy.context.scene.eevee.motion_blur_steps"]

    class EeveeVolumetrics(Settings):
        full_data_paths = ["bpy.context.scene.eevee.volumetric_start",
                           "bpy.context.scene.eevee.volumetric_end",
                           "bpy.context.scene.eevee.volumetric_tile_size",
                           "bpy.context.scene.eevee.volumetric_samples",
                           "bpy.context.scene.eevee.volumetric_sample_distribution",
                           "bpy.context.scene.eevee.use_volumetric_lights",
                           "bpy.context.scene.eevee.volumetric_light_clamp",
                           "bpy.context.scene.eevee.use_volumetric_shadows",
                           "bpy.context.scene.eevee.volumetric_shadow_samples"]

    class EeveeShadows(Settings):
        full_data_paths = ["bpy.context.scene.eevee.shadow_cube_size",
                           "bpy.context.scene.eevee.shadow_cascade_size",
                           "bpy.context.scene.eevee.use_shadow_high_bitdepth",
                           "bpy.context.scene.eevee.use_soft_shadows",
                           "bpy.context.scene.eevee.light_threshold"]

    class EeveeIndirectLightning(Settings):
        full_data_paths = ["bpy.context.scene.eevee.gi_auto_bake",
                           "bpy.context.scene.eevee.gi_diffuse_bounces",
                           "bpy.context.scene.eevee.gi_cubemap_resolution",
                           "bpy.context.scene.eevee.gi_visibility_resolution",
                           "bpy.context.scene.eevee.gi_irradiance_smoothing",
                           "bpy.context.scene.eevee.gi_glossy_clamp",
                           "bpy.context.scene.eevee.gi_filter_quality",
                           "bpy.context.scene.eevee.gi_cubemap_display_size",
                           "bpy.context.scene.eevee.gi_show_cubemaps",
                           "bpy.context.scene.eevee.gi_irradiance_display_size",
                           "bpy.context.scene.eevee.gi_show_irradiance"]

    data_id: str
    name: str
    version: tuple

    eevee_sampling: EeveeSampling
    eevee_bloom: EeveeBloom
    eevee_DOF: EeveeDOF
    eevee_AO: EeveeAO
    eevee_SSS: EeveeSSS
    eevee_SSR: EeveeSSR
    eevee_motion_blur: EeveeMotionBlur
    eevee_volumetrics: EeveeVolumetrics
    eevee_shadows: EeveeShadows
    eevee_indirect_lightning: EeveeIndirectLightning

    performance: Performance
    curves: Curves
    film: Film
    simplify: Simplify
    grease_pencil: GreasePencil
    freestyle: Freestyle
    color_management: ColorManagement

    eevee_settings: list[Settings]

    def __init__(self, name="") -> None:
        self.version = RENDERSETTINGS_VERSION
        self.data_id = "FTB Render Settings"
        self.name = name
        self.eevee_sampling = self.EeveeSampling()
        self.eevee_AO = self.EeveeAO()
        self.eevee_SSS = self.EeveeSSS()
        self.eevee_bloom = self.EeveeBloom()
        self.eevee_DOF = self.EeveeDOF()
        self.eevee_SSR = self.EeveeSSR()
        self.eevee_motion_blur = self.EeveeMotionBlur()
        self.eevee_volumetrics = self.EeveeVolumetrics()
        self.eevee_shadows = self.EeveeShadows()
        self.eevee_indirect_lightning = self.EeveeIndirectLightning()
        self.performance = self.Performance()
        self.curves = self.Curves()
        self.grease_pencil = self.GreasePencil()
        self.freestyle = self.Freestyle()
        self.film = self.Film()
        self.simplify = self.Simplify()
        self.color_management = self.ColorManagement()

        self.eevee_settings = [self.eevee_sampling, self.eevee_AO, self.eevee_SSS, self.eevee_bloom, self.eevee_DOF,
                               self.eevee_SSR, self.eevee_motion_blur, self.eevee_volumetrics, self.eevee_shadows,
                               self.eevee_indirect_lightning, self.performance, self.curves, self.film, self.simplify,
                               self.grease_pencil, self.freestyle, self.color_management]

    def load_eevee_settings(self) -> None:
        for category in self.eevee_settings:
            category.load()

    def __str__(self) -> str:
        categories_str: str = [category.__str__() for category in self.eevee_settings]
        return (f"Render Settings\n"
                f"{{\n"
                f"{''.join(categories_str)}\n"
                f"}}\n")
