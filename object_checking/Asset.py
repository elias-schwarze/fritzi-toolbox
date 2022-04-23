import bpy
from bpy.types import Collection, Object

bChecked: bool = False

bFileIsClean: bool =  False
bFileInWorkspace: bool = False
bPropIDFileName: bool = False
bProperFileName: bool = False

PropCollection: Collection = None
PropCollectionOverride: Collection = None
bPropIDCollectionName: bool = False
bProperCollectionName: bool = False

PropEmpty: Object = None
bPropIDEmptyName: bool = False
bProperEmptyName: bool = False
bEmptyOnWorldOrigin: bool = False

bEqualFileCollectionName: bool = False
bEqualFileEmptyName: bool = False
bEqualCollectonEmptyName: bool = False
bEqualNaming: bool = False

SubDLevelErrors: list = []
ApplyScaleErrors: list  = []
MissingSlotErrors: list  = []
SlotLinkErrors: list  = []
UnusedSlotErrors: list  = []
ParentingErrors: list  = []
NGonErrors: list  = []
RogueObjectErrors: list  = []
MissingDisplacementErrors: list  = []

def InitializeCheck(self):
    self.bFileIsClean = False
    self.bFileInWorkspace = False
    self.bPropIDFileName = False
    self.bProperFileName = False

    self.PropCollection = None
    self.bPropIDCollectionName = False
    self.bProperCollectionName = False

    self.PropEmpty = None
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
    self.MissingDisplacementErrors = []

def HasFileErrors():
    return not(bFileInWorkspace and bPropIDFileName and bProperFileName and bFileIsClean)

def HasCollectionErrors():
    return not(PropCollection and bEqualFileCollectionName and bProperCollectionName 
                and bPropIDCollectionName)

def HasEmptyErrors():
    return not(PropEmpty and bEmptyOnWorldOrigin and bEqualFileEmptyName and 
                bEqualCollectonEmptyName and bPropIDEmptyName and bProperEmptyName)

def HasObjectErrors():
    return RogueObjectErrors or SubDLevelErrors or MissingDisplacementErrors or \
            ApplyScaleErrors or NGonErrors or MissingSlotErrors or \
            SlotLinkErrors or UnusedSlotErrors or ParentingErrors

def IsSaved():
    return bpy.data.is_saved and bpy.data.filepath != ''
