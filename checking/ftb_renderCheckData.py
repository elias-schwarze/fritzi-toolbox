from dataclasses import dataclass


@dataclass
class RenderCheckData:
    """A class that can contain all relevant render settings and methods to compare against defaults for render check."""

    framerate : int = 50
    resX : int = 3840
    resY : int = 2160
    resPercent : int = 100

    casShadow : str = '4096'
    cubeShadow : str = '4096'
    highBitShadow : bool = True
    softShadow : bool = True

    useAo : bool = True
    aoDist : float = 0.5
    aoFactor : float = 1.0
    aoQuality :float = 1.0
    aoBentNormals : bool = True
    aoBounce : bool = True

    overscan : bool = True
    oversize : float = 5.0

    outFormat : str = 'OPEN_EXR_MULTILAYER'
    outColor : str = 'RGBA'
    outDepth : str = '32'
    outCodec : str = 'ZIP'

    invalidBoolObjects : list = None

    def getResText(self):
        """Build a string that can be displayed in a Ui label, contains information about resolution and framerate
        Returns: string"""

        return (str(self.resX) + " x " + str(self.resY) + " x "+ str(self.resPercent) + "% @ " + str(self.framerate) + "fps")

    def matchResFps(self, matchData):
        """"Returns True if resolution and framerate of this instance matches with provided matchData"""

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
        """"Returns True if shadow settings of this instance matches with provided matchData instance."""

        matchCascade = matchData.casShadow == self.casShadow
        matchCube = matchData.cubeShadow == self.cubeShadow
        matchHighBitDepth = matchData.highBitShadow == self.highBitShadow
        matchSoftShadows = matchData.softShadow == self.softShadow

        if all([matchCascade, matchCube, matchHighBitDepth, matchSoftShadows]):
            return True
        else:
            return False

    def getAoText(self):
        """Build tuple of strings that can be displayed in a Ui label, contains information about ambient occlusion
        Returns: tuple[useAo, aoDist, aoFactor, aoQuality, aoBentNormals, aoBounce]"""
        useAoDist = "Use AO: " + str(self.useAo) + " || " + "Distance: " + str( '%.2f' % self.aoDist)
        aoFactorQuality = "Factor: " + str( '%.2f' % self.aoFactor) + " || " + "Quality: " + str( '%.2f' % self.aoQuality)
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