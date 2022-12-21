import bpy

from .. utility_functions.ftb_string_utils import WORKSPACE_ROOT

bChecked: bool = False

bFileIsClean: bool = False
bPropIDFileName: bool = False
bProperFileName: bool = False

bPropIDCollectionName: bool = False
bProperCollectionName: bool = False

bPropIDEmptyName: bool = False
bProperEmptyName: bool = False
bEmptyOnWorldOrigin: bool = False

bEqualFileCollectionName: bool = False
bEqualFileEmptyName: bool = False
bEqualCollectonEmptyName: bool = False
bEqualNaming: bool = False

SubDLevelErrors: list = []
ApplyScaleErrors: list = []
MissingSlotErrors: list = []
SlotLinkErrors: list = []
UnusedSlotErrors: list = []
ParentingErrors: list = []
NGonErrors: list = []
RogueObjectErrors: list = []
DisplacementErrors: list = []
InvalidNameErrors: list = []

ApplyRotNotification: list = []
MissingDisplacementNotification: list = []
MissingShapeKeysNotification: list = []


def InitializeCheck(self):
    self.bFileIsClean = False
    self.bPropIDFileName = False
    self.bProperFileName = False

    self.bPropIDCollectionName = False
    self.bProperCollectionName = False

    self.bPropIDEmptyName = False
    self.bProperEmptyName = False
    self.bEmptyOnWorldOrigin = False

    self.bEqualFileCollectionName = False
    self.bEqualFileEmptyName = False
    self.bEqualCollectonEmptyName = False
    self.bEqualNaming = False

    self.SubDLevelErrors = []
    self.ApplyScaleErrors = []
    self.MissingSlotErrors = []
    self.SlotLinkErrors = []
    self.UnusedSlotErrors = []
    self.ParentingErrors = []
    self.NGonErrors = []
    self.RogueObjectErrors = []
    self.DisplacementErrors = []
    self.InvalidNameErrors = []

    self.ApplyRotNotification = []
    self.MissingDisplacementNotification = []
    self.MissingShapeKeysNotification = []


def IsFileInWorkspace():
    if not IsSaved():
        return False

    if bpy.data.filepath.find(WORKSPACE_ROOT) != -1:
        return True

    return False


def IsPropEmpty(Empty: bpy.types.Object):
    return Empty.type == 'EMPTY' and not(Empty.library or Empty.override_library or Empty.instance_collection or Empty.field)


def GetFileErrorCount():
    return int(not(IsFileInWorkspace())) + int(not(bProperFileName)) + \
           int(not(bPropIDFileName)) + int(not(bFileIsClean))


def GetCollectionErrorCount():
    return int(not(bEqualFileCollectionName)) + int(not(bProperCollectionName)) + \
           int(not(bPropIDCollectionName)) + int(not(bpy.context.window_manager.PropCollectionReference))


def GetEmptyErrorCount():
    return int(not(bpy.context.window_manager.PropEmptyReference)) + int(not(bEmptyOnWorldOrigin)) + \
           int(not(bEqualFileEmptyName)) + int(not(bEqualCollectonEmptyName)) + int(not(bPropIDEmptyName)) + \
           int(not(bProperEmptyName))


def GetObjectErrorCount():
    return len(RogueObjectErrors) + len(SubDLevelErrors) + len(ParentingErrors) + \
           len(ApplyScaleErrors) + len(NGonErrors) + len(MissingSlotErrors) + \
           len(SlotLinkErrors) + len(UnusedSlotErrors) + len(InvalidNameErrors) + \
           len(DisplacementErrors)


def GetTotalNotificationCount():
    return len(ApplyRotNotification) + len(MissingShapeKeysNotification) + len(MissingDisplacementNotification)


def GetTotalErrorCount():
    return GetFileErrorCount() + GetCollectionErrorCount() + GetEmptyErrorCount() + GetObjectErrorCount()


def HasFileErrors():
    return not(IsFileInWorkspace() and bPropIDFileName and bProperFileName and bFileIsClean)


def HasCollectionErrors():
    return not(bpy.context.window_manager.PropCollectionReference and bEqualFileCollectionName
               and bProperCollectionName and bPropIDCollectionName)


def HasEmptyErrors():
    return not(bpy.context.window_manager.PropEmptyReference and bEmptyOnWorldOrigin and bEqualFileEmptyName and
               bEqualCollectonEmptyName and bPropIDEmptyName and bProperEmptyName)


def HasObjectErrors():
    return RogueObjectErrors or SubDLevelErrors or ParentingErrors or \
           ApplyScaleErrors or NGonErrors or MissingSlotErrors or \
           SlotLinkErrors or UnusedSlotErrors or InvalidNameErrors or \
           DisplacementErrors


def HasNotifications():
    return ApplyRotNotification or MissingShapeKeysNotification or MissingDisplacementNotification


def IsSaved():
    return bpy.data.is_saved and bpy.data.filepath
