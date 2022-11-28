import bpy

RENDERSETTINGS_VERSION = (0, 9, 5)


class RenderSettings:

    class Film:
        filter_size: float
        film_transparent: bool
        use_overscan: bool
        overscan_size: float

        def __init__(self) -> None:
            eevee = bpy.context.scene.eevee
            render = bpy.context.scene.render
            self.filter_size = render.filter_size
            self.film_transparent = render.film_transparent
            self.use_overscan = eevee.use_overscan
            self.overscan_size = eevee.overscan_size

        def __str__(self) -> str:
            return (f"\tFilm\n"
                    f"\t{{\n"
                    f"\t\tFilter Size = {self.filter_size}\n"
                    f"\t\tTransparent = {self.film_transparent}\n"
                    f"\t\tOverscan = {self.use_overscan}\n"
                    f"\t\tOverscan Size = {self.overscan_size}\n"
                    f"\t}}\n"
                    )

    class Simplify:
        use_simplify: bool
        simplify_subdivision: int
        simplify_child_particles: float
        simplify_volumes: float
        simplify_subdivision_render: int
        simplify_child_particles_render: float
        simplify_gpencil: bool
        simplify_gpencil_onplay: bool
        simplify_gpencil_view_fill: bool
        simplify_gpencil_modifier: bool
        simplify_gpencil_shader_fx: bool
        simplify_gpencil_tint: bool
        simplify_gpencil_antialiasing: bool

        def __init__(self) -> None:
            render = bpy.context.scene.render
            self.use_simplify = render.use_simplify
            self.simplify_subdivision = render.simplify_subdivision
            self.simplify_child_particles = render.simplify_child_particles
            self.simplify_volumes = render.simplify_volumes
            self.simplify_subdivision_render = render.simplify_subdivision_render
            self.simplify_child_particles_render = render.simplify_child_particles_render
            self.simplify_gpencil = render.simplify_gpencil
            self.simplify_gpencil_onplay = render.simplify_gpencil_onplay
            self.simplify_gpencil_view_fill = render.simplify_gpencil_view_fill
            self.simplify_gpencil_modifier = render.simplify_gpencil_modifier
            self.simplify_gpencil_shader_fx = render.simplify_gpencil_shader_fx
            self.simplify_gpencil_tint = render.simplify_gpencil_tint
            self.simplify_gpencil_antialiasing = render.simplify_gpencil_antialiasing

        def __str__(self) -> str:
            return (f"\tSimplify = {self.use_simplify}\n"
                    f"\t{{\n"
                    f"\t\tViewport Subdivision = {self.simplify_subdivision}\n"
                    f"\t\tViewport Max Child Particles = {self.simplify_child_particles}\n"
                    f"\t\tViewport Volume Resolution = {self.simplify_volumes}\n"
                    f"\t\tRender Subdivision = {self.simplify_subdivision_render}\n"
                    f"\t\tRender Max Child Particles = {self.simplify_child_particles_render}\n"
                    f"\t\tGrease Pencil Simplify = {self.simplify_gpencil}\n"
                    f"\t\tGP Playback Only = {self.simplify_gpencil_onplay}\n"
                    f"\t\tGP Fill = {self.simplify_gpencil_view_fill}\n"
                    f"\t\tGP Modifiers = {self.simplify_gpencil_modifier}\n"
                    f"\t\tGP Shader Effects = {self.simplify_gpencil_shader_fx}\n"
                    f"\t\tGP Layer Tint = {self.simplify_gpencil_tint}\n"
                    f"\t\tGP Antialiasing = {self.simplify_gpencil_antialiasing}\n"
                    f"\t}}\n"
                    )

    # @dataclass
    class ColorManagement:
        display_device: str
        view_transform: str
        look: str
        exposure: float
        gamma: float
        name: str

        def __init__(self) -> None:
            display_settings = bpy.context.scene.display_settings
            view_settings = bpy.context.scene.view_settings
            sequencer_colorspace_settings = bpy.context.scene.sequencer_colorspace_settings
            self.display_device = display_settings.display_device
            self.view_transform = view_settings.view_transform
            self.look = view_settings.look
            self.exposure = view_settings.exposure
            self.gamma = view_settings.gamma
            self.name = sequencer_colorspace_settings.name

        def __str__(self) -> str:
            return (f"\tColor Management\n"
                    f"\t{{\n"
                    f"\t\tDisplay Device = {self.display_device}\n"
                    f"\t\tView Transform = {self.view_transform}\n"
                    f"\t\tLook = {self.look}\n"
                    f"\t\tExposure = {self.exposure}\n"
                    f"\t\tGamma = {self.gamma}\n"
                    f"\t\tSequencer = {self.name}\n"
                    f"\t}}\n"
                    )

    # @dataclass
    class EeveeSampling:
        taa_render_samples: int
        taa_samples: int
        use_taa_reprojection: bool

        def __init__(self) -> None:
            eevee = bpy.context.scene.eevee
            self.taa_render_samples = eevee.taa_render_samples
            self.taa_samples = eevee.taa_samples
            self.use_taa_reprojection = eevee.use_taa_reprojection

        def __str__(self) -> str:
            return (f"\tEevee Sampling\n"
                    f"\t{{\n"
                    f"\t\tRender Samples = {self.taa_render_samples}\n"
                    f"\t\tViewport Samples = {self.taa_samples}\n"
                    f"\t\tViewport Denoising = {self.use_taa_reprojection}\n"
                    f"\t}}\n"
                    )

    # @dataclass
    class EeveeAO:
        use_gtao: bool
        gtao_distance: float
        gtao_factor: float
        gtao_quality: float
        use_gtao_bent_normals: bool
        use_gtao_bounce: bool

        def __init__(self) -> None:
            eevee = bpy.context.scene.eevee
            self.use_gtao = eevee.use_gtao
            self.gtao_distance = eevee.gtao_distance
            self.gtao_factor = eevee.gtao_factor
            self.gtao_quality = eevee.gtao_quality
            self.use_gtao_bent_normals = eevee.use_gtao_bent_normals
            self.use_gtao_bounce = eevee.use_gtao_bounce

        def __str__(self) -> str:
            return (f"\tAmbient Occlusion = {self.use_gtao}\n"
                    f"\t{{\n"
                    f"\t\tDistance = {self.gtao_distance}\n"
                    f"\t\tFactor = {self.gtao_factor}\n"
                    f"\t\tTrace Precision = {self.gtao_quality}\n"
                    f"\t\tBent Normals = {self.use_gtao_bent_normals}\n"
                    f"\t\tBounces Approximation = {self.use_gtao_bent_normals}\n"
                    f"\t}}\n"
                    )

    # @dataclass
    class EeveeSSR:
        use_ssr: bool
        use_ssr_refraction: bool
        use_ssr_halfres: bool
        ssr_quality: float
        ssr_max_roughness: float
        ssr_thickness: float
        ssr_border_fade: float
        ssr_firefly_fac: float

        def __init__(self) -> None:
            eevee = bpy.context.scene.eevee
            self.use_ssr = eevee.use_ssr
            self.use_ssr_refraction = eevee.use_ssr_refraction
            self.use_ssr_halfres = eevee.use_ssr_halfres
            self.ssr_quality = eevee.ssr_quality
            self.ssr_max_roughness = eevee.ssr_max_roughness
            self.ssr_thickness = eevee.ssr_thickness
            self.ssr_border_fade = eevee.ssr_border_fade
            self.ssr_firefly_fac = eevee.ssr_firefly_fac

        def __str__(self) -> str:
            return (f"\tScreen Space Reflections = {self.use_ssr}\n"
                    f"\t{{\n"
                    f"\t\tUse Refraction = {self.use_ssr_refraction}\n"
                    f"\t\tFactor = {self.use_ssr_halfres}\n"
                    f"\t\tTrace Precision = {self.ssr_quality}\n"
                    f"\t\tMax Roughness = {self.ssr_max_roughness}\n"
                    f"\t\tThickness = {self.ssr_thickness}\n"
                    f"\t\tEdge Fading = {self.ssr_border_fade}\n"
                    f"\t\tClamp = {self.ssr_firefly_fac}\n"
                    f"\t}}\n"
                    )

    # @dataclass
    class EeveeVolumetrics:
        volumetric_start: float
        volumetric_end: float
        volumetric_tile_size: str
        volumetric_samples: int
        volumetric_sample_distribution: float
        use_volumetric_lights: bool
        volumetric_light_clamp: float
        use_volumetric_shadows: bool
        volumetric_shadow_samples: int

        def __init__(self) -> None:
            eevee = bpy.context.scene.eevee
            self.volumetric_start = eevee.volumetric_start
            self.volumetric_end = eevee.volumetric_end
            self.volumetric_tile_size = eevee.volumetric_tile_size
            self.volumetric_samples = eevee.volumetric_samples
            self.volumetric_sample_distribution = eevee.volumetric_sample_distribution
            self.use_volumetric_lights = eevee.use_volumetric_lights
            self.volumetric_light_clamp = eevee.volumetric_light_clamp
            self.use_volumetric_shadows = eevee.use_volumetric_shadows
            self.volumetric_shadow_samples = eevee.volumetric_shadow_samples

        def __str__(self) -> str:
            return (f"\tEevee Volumetrics\n"
                    f"\t{{\n"
                    f"\t\tStart = {self.volumetric_start}\n"
                    f"\t\tEnd = {self.volumetric_end}\n"
                    f"\t\tTile Size = {self.volumetric_tile_size}\n"
                    f"\t\tSamples = {self.volumetric_samples}\n"
                    f"\t\tDistribution = {self.volumetric_sample_distribution}\n"
                    f"\t\tUse Volumetric Lights = {self.use_volumetric_lights}\n"
                    f"\t\tVolumetric Light Clamp = {self.volumetric_light_clamp}\n"
                    f"\t\tUse Volumetric Shadows = {self.use_volumetric_shadows}\n"
                    f"\t\tShadow Samples = {self.volumetric_shadow_samples}\n"
                    f"\t}}\n"
                    )

    # @dataclass
    class EeveeShadows:
        shadow_cube_size: str
        shadow_cascade_size: str
        use_shadow_high_bitdepth: bool
        use_soft_shadows: bool
        light_threshold: float

        def __init__(self) -> None:
            eevee = bpy.context.scene.eevee
            self.shadow_cube_size = eevee.shadow_cube_size
            self.shadow_cascade_size = eevee.shadow_cascade_size
            self.use_shadow_high_bitdepth = eevee.use_shadow_high_bitdepth
            self.use_soft_shadows = eevee.use_soft_shadows
            self.light_threshold = eevee.light_threshold

        def __str__(self) -> str:
            return (f"\tEevee Shadows\n"
                    f"\t{{\n"
                    f"\t\tCube Size = {self.shadow_cube_size}\n"
                    f"\t\tCascade Size = {self.shadow_cascade_size}\n"
                    f"\t\tHigh Bit Deptj = {self.use_shadow_high_bitdepth}\n"
                    f"\t\tUse Soft Shadows = {self.use_soft_shadows}\n"
                    f"\t\tLight Treshold = {self.light_threshold}\n"
                    f"\t}}\n"
                    )

    # @dataclass
    class EeveeIndirectLightning:
        gi_auto_bake: bool
        gi_diffuse_bounces: int
        gi_cubemap_resolution: str
        gi_visibility_resolution: str
        gi_irradiance_smoothing: float
        gi_glossy_clamp: float
        gi_filter_quality: float
        gi_cubemap_display_size: float
        gi_show_cubemaps: bool
        gi_irradiance_display_size: float
        gi_show_irradiance: bool

        def __init__(self) -> None:
            eevee = bpy.context.scene.eevee
            self.gi_auto_bake = eevee.gi_auto_bake
            self.gi_diffuse_bounces = eevee.gi_diffuse_bounces
            self.gi_cubemap_resolution = eevee.gi_cubemap_resolution
            self.gi_visibility_resolution = eevee.gi_visibility_resolution
            self.gi_irradiance_smoothing = eevee.gi_irradiance_smoothing
            self.gi_glossy_clamp = eevee.gi_glossy_clamp
            self.gi_filter_quality = eevee.gi_filter_quality
            self.gi_cubemap_display_size = eevee.gi_cubemap_display_size
            self.gi_show_cubemaps = eevee.gi_show_cubemaps
            self.gi_irradiance_display_size = eevee.gi_irradiance_display_size
            self.gi_show_irradiance = eevee.gi_show_irradiance

        def __str__(self) -> str:
            return (f"\tIndirect Lightning\n"
                    f"\t{{\n"
                    f"\t\tAuto Bake = {self.gi_auto_bake}\n"
                    f"\t\tDiffuse Bounces = {self.gi_diffuse_bounces}\n"
                    f"\t\tCubemap Size = {self.gi_cubemap_resolution}\n"
                    f"\t\tDiffuse Occlusion = {self.gi_visibility_resolution}\n"
                    f"\t\tIrradiance Smoothing = {self.gi_irradiance_smoothing}\n"
                    f"\t\tClamp Glossy = {self.gi_glossy_clamp}\n"
                    f"\t\tFilter Quality = {self.gi_filter_quality}\n"
                    f"\t\tShow Cubemaps = {self.gi_show_cubemaps}\n"
                    f"\t\tCubemap Size = {self.gi_cubemap_display_size}\n"
                    f"\t\tShow Irradiance = {self.gi_show_irradiance}\n"
                    f"\t\tIrradiance Size = {self.gi_irradiance_display_size}\n"
                    f"\t}}\n"
                    )
    data_id: str
    version: tuple

    eevee_sampling: EeveeSampling
    eevee_AO: EeveeAO
    eevee_SSR: EeveeSSR
    eevee_volumetrics: EeveeVolumetrics
    eevee_shadows: EeveeShadows
    eevee_indirect_lightning: EeveeIndirectLightning

    film: Film

    simplify: Simplify

    color_management: ColorManagement

    def __init__(self) -> None:
        self.version = RENDERSETTINGS_VERSION
        self.data_id = "FTB Render Settings"
        self.eevee_sampling = self.EeveeSampling()
        self.eevee_AO = self.EeveeAO()
        self.eevee_SSR = self.EeveeSSR()
        self.eevee_volumetrics = self.EeveeVolumetrics()
        self.eevee_shadows = self.EeveeShadows()
        self.eevee_indirect_lightning = self.EeveeIndirectLightning()
        self.film = self.Film()
        self.simplify = self.Simplify()
        self.color_management = self.ColorManagement()

    def __str__(self) -> str:
        categories = [self.eevee_sampling, self.eevee_AO, self.eevee_SSR, self.eevee_volumetrics, self.eevee_shadows,
                      self.eevee_indirect_lightning, self.film, self.simplify, self.color_management]
        categories_str: str = [category.__str__() for category in categories]
        return (f"Render Settings\n"
                f"{{\n"
                f"{''.join(categories_str)}\n"
                f"}}\n")

    # viewe layer confoguration rendering
    # volume light
    # environment
    # cryptomatte object+ asset
