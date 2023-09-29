from dataclasses import dataclass, field


@dataclass
class RenderCheckData:
    """A class that can contain all relevant render settings and methods to compare against defaults for render check."""

    framerate: int = 50
    resX: int = 1920
    resY: int = 1080
    resPercent: int = 100

    renderSamples: int = 200

    casShadow: str = '4096'
    cubeShadow: str = '4096'
    highBitShadow: bool = True
    softShadow: bool = True

    useAo: bool = True
    aoDist: float = 0.5
    aoFactor: float = 1.0
    aoQuality: float = 1.0
    aoBentNormals: bool = True
    aoBounce: bool = True

    overscan: bool = True
    oversize: float = 5.0

    outFormat: str = 'OPEN_EXR_MULTILAYER'
    outColor: str = 'RGBA'
    outDepth: str = '16'
    outCodec: str = 'ZIP'

    cmDisplayDevice = 'sRGB'
    cmViewTransform = 'Filmic'
    cmLook = 'None'
    cmExposure = 0.0
    cmGamma = 1.0

    invalidBoolObjects: list = field(default_factory=list)

    invalidNlaObjects: list = field(default_factory=list)

    invalid_data_transfer_objects: list = field(default_factory=list)

    modifier_visibility_issues: list = field(default_factory=list)

    isBurnInActive: bool = False

    totalViewLayerCount: int = 0
    activeViewLayerCount: int = 0

    render_single_layer: bool = False
    film_transparent: bool = True

    simplify_subdiv_render: int = 6

    uncOutput: bool = True
    uncProject: bool = True

    use_compositing: bool = False
    use_sequencer: bool = False

    use_bloom: bool = False

    cry_object_pass: bool = True
    cry_asset_pass: bool = True
    cry_levels: int = 2
    cry_accurate: bool = True

    aovs = {
        "VectorLightMask": "VALUE",
        "DiffuseLightMask": "VALUE",
        "VectorRimLightMask": "VALUE",
        "VectorHighLightMask": "VALUE",
        "DiffuseRimLightMask": "VALUE",
        "DiffuseHighLightMask": "VALUE",
        "charNormal": "COLOR",
        "matte_glasses": "VALUE"
    }

    cryptoLayerName = "3d"
    cryptoLayerExists = False

    def matchAovs(self, matchData) -> bool:
        """Returns True if all AOVs of this dataclass are contained in the target scene and have the same value"""
        matchAov: bool = True

        if not matchData:
            matchAov = False
            return matchAov

        if not self.aovs:
            matchAov = False
            return matchAov

        if len(self.aovs) == 0:
            matchAov = False
            return matchAov

        for key in matchData.aovs:
            if key not in self.aovs:
                matchAov = False
                return matchAov

            else:
                if self.aovs[key] != matchData.aovs[key]:
                    matchAov = False
                    return matchAov

        return matchAov

    def getResText(self):
        """Build a string that can be displayed in a Ui label, contains information about resolution and framerate
        Returns: string"""

        return (str(self.resX) + " x " + str(self.resY) + " x " + str(self.resPercent) + "% @ " + str(self.framerate) + "fps")

    def getSamplesText(self):
        """Build display string for sample count"""

        return "Samples: " + str(self.renderSamples)

    def matchResFps(self, matchData):
        """Returns True if resolution and framerate of this instance matches with provided matchData"""

        matchResX = matchData.resX == self.resX
        matchResY = matchData.resY == self.resY
        matchResPercent = matchData.resPercent == self.resPercent
        matchFramerate = matchData.framerate == self.framerate

        if all([matchResX, matchResY, matchResPercent, matchFramerate]):
            return True
        else:
            return False

    def getShadowsText(self):
        """Build tuple of strings that can be displayed in a Ui label, contains information about shadow resolution
        Returns: tuple[cascadeShadow : str, cubeShadow : str, highBit : str, softShadow : str,]"""

        ShadowResText = "Cascade: " + str(self.casShadow) + " || " + "Cube: " + str(self.cubeShadow)
        ShadowMiscTex = "High Bit: " + str(self.highBitShadow) + " || " + "Soft: " + str(self.softShadow)

        return (ShadowResText, ShadowMiscTex,)

    def matchShadows(self, matchData):
        """Returns True if shadow settings of this instance matches with provided matchData instance."""

        matchCascade = matchData.casShadow == self.casShadow
        matchCube = matchData.cubeShadow == self.cubeShadow
        matchHighBitDepth = matchData.highBitShadow == self.highBitShadow
        matchSoftShadows = matchData.softShadow == self.softShadow

        if all([matchCascade, matchCube, matchHighBitDepth, matchSoftShadows]):
            return True
        else:
            return False

    def matchSamples(self, matchData):
        """Returns true if number of render samples match with provided matchData instance"""
        return matchData.renderSamples == self.renderSamples

    def getAoText(self):
        """Build tuple of strings that can be displayed in a Ui label, contains information about ambient occlusion
        Returns: tuple[useAo, aoDist, aoFactor, aoQuality, aoBentNormals, aoBounce]"""
        useAoDist = "Use AO: " + str(self.useAo) + " || " + "Distance: " + str('%.2f' % self.aoDist)
        aoFactorQuality = "Factor: " + str('%.2f' % self.aoFactor) + " || " + "Quality: " + str('%.2f' % self.aoQuality)
        aoSettings = "Bent: " + str(self.aoBentNormals) + " || " + "Bounce: " + str(self.aoBounce)
        return (useAoDist, aoFactorQuality, aoSettings)

    def matchAo(self, matchData):
        """Returns True if ambient occlusion settings of this instance matches with provided matchData instance."""

        matchAoOn = matchData.useAo == self.useAo
        matchAoDist = matchData.aoDist == self.aoDist
        matchAoFactor = matchData.aoFactor == self.aoFactor
        matchAoQuality = matchData.aoQuality == self.aoQuality
        matchAoBentNormals = matchData.aoBentNormals == self.aoBentNormals
        matchAoBounce = matchData.aoBounce == self.aoBounce

        if all([matchAoOn, matchAoDist, matchAoFactor, matchAoQuality, matchAoBentNormals, matchAoBounce]):
            return True
        else:
            return False

    def getOutParamsText(self):
        """Build a string that can be displayed in a Ui label, contains information about resolution and framerate
        Returns: string"""
        outFormatText = "Format: " + self.outFormat
        outColorDepthText = "Color: " + self.outColor + " @ " + self.outDepth + "bit"
        outCodec = "Codec: " + self.outCodec

        return (outFormatText, outColorDepthText, outCodec)

    def matchOutput(self, matchData):
        """Returns True if output format settings of this instance matches with provided matchData instance."""
        matchOutFormat = matchData.outFormat == self.outFormat
        matchOutColor = matchData.outColor == self.outColor
        matchOutDepth = matchData.outDepth == self.outDepth
        matchOutCodec = matchData.outCodec == self.outCodec

        if all([matchOutFormat, matchOutColor, matchOutDepth, matchOutCodec]):
            return True
        else:
            return False

    def getCmText(self):
        """Build a string that can be displayed in UI, contains Color Management settings
        Returns: string"""
        outCmText = self.cmDisplayDevice + ", " + self.cmViewTransform + ", " + self.cmLook
        outCmParams = "Exposure: " + str(self.cmExposure) + ", Gamma: " + str(self.cmGamma)

        return (outCmText, outCmParams)

    def matchColorMangement(self, matchData):
        """Returns True if color management settings of this instance matches with provided matchData instance."""
        matchCmDisplayDevice = matchData.cmDisplayDevice == self.cmDisplayDevice
        matchCmViewTransform = matchData.cmViewTransform == self.cmViewTransform
        matchCmLook = matchData.cmLook == self.cmLook
        matchCmExposure = matchData.cmExposure == self.cmExposure
        matchCmGamma = matchData.cmGamma == self.cmGamma

        if all([matchCmDisplayDevice, matchCmViewTransform, matchCmLook, matchCmExposure, matchCmGamma]):
            return True
        else:
            return False

    def matchCryptomatte(self, matchData):
        """Returns True if cryptomatte settings match with provided matchData instance"""
        matchObject = matchData.cry_object_pass == self.cry_object_pass
        matchAsset = matchData.cry_asset_pass == self.cry_asset_pass
        matchAccurate = matchData.cry_accurate == self.cry_accurate
        matchLevels = matchData.cry_levels == self.cry_levels

        if all([matchObject, matchAsset, matchAccurate, matchLevels]):
            return True
        else:
            return False