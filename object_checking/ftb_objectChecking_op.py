import os
import math
import re
import bpy

from bpy.app.handlers import persistent
from bpy.types import Operator
from bpy.props import BoolProperty

#D = bpy.data
TRESHOLD = 0.001
INVALID_CHARS = ["ä", "Ä", "ü", "Ü", "ö", "Ö", "ß", ":", ")", "("]
ROGUE_OBJECTS = ['CAMERA', 'LIGHT', 'GPENCIL', 'LIGHT', 'LIGHT_PROBE', 'SPEAKER']
OS_SEPARATOR = os.sep

class AssetChecker:

    bFileIsClean: bool
    bFileInWorkspace = False
    bPropIDFileName = False
    bProperFileName = False

    PropCollection = None
    PropCollectionOverride = None
    bPropIDCollectionName = False
    bProperCollectionName = False

    PropEmpty = None
    bPropIDEmptyName = False
    bProperEmptyName = False
    bEmptyOnWorldOrigin = False

    bEqualFileCollectionName = False
    bEqualFileEmptyName = False
    bEqualCollectonEmptyName = False
    bEqualNaming = False

    SubDLevelErrors = []
    ApplyScaleErrors = []
    MissingSlotErrors = []
    SlotLinkErrors = []
    UnusedSlotErrors = []
    ParentingErrors = []
    NGonErrors = []
    RogueObjectErrors = []
    MissingDisplacementErrors = []

    def Initialize(self):
        AssetChecker.bFileIsClean = False
        AssetChecker.bFileInWorkspace = False
        AssetChecker.bPropIDFileName = False
        AssetChecker.bProperFileName = False

        AssetChecker.PropCollection = None
        AssetChecker.bPropIDCollectionName = False
        AssetChecker.bProperCollectionName = False

        AssetChecker.PropEmpty = None
        AssetChecker.bPropIDEmptyName = False
        AssetChecker.bProperEmptyName = False
        AssetChecker.bEmptyOnWorldOrigin = False

        AssetChecker.bEqualFileCollectionName = False
        AssetChecker.bEqualFileEmptyName = False
        AssetChecker.bEqualCollectonEmptyName = False
        AssetChecker.bEqualNaming = False

        AssetChecker.SubDLevelErrors = []
        AssetChecker.ApplyScaleErrors = []
        AssetChecker.MissingSlotErrors = []
        AssetChecker.SlotLinkErrors = []
        AssetChecker.UnusedSlotErrors = []
        AssetChecker.ParentingErrors = []
        AssetChecker.NGonErrors = []
        AssetChecker.RogueObjectErrors = []
        AssetChecker.MissingDisplacementErrors = []

@persistent
def DepsgraphCustomUpdate(self, context):
    #AssetChecker.bFileInWorkspace = IsFileInWorkspace()
    pass

def IsFileInWorkspace():
    if not bpy.data.is_saved or bpy.data.filepath == "":
        return False

    if bpy.data.filepath.find("fritzi_serie") == -1:
        return False

    return True

def IsFileClean():
    if len(bpy.data.libraries) > 0:
        return False
    # TODO: check for 0 users
    return True

def IsOnWorldOrigin(Object: bpy.types.Object):
    return math.isclose(Object.location[0], 0, abs_tol = TRESHOLD) and math.isclose(Object.location[1], 0, abs_tol = TRESHOLD) and math.isclose(Object.location[2], 0, abs_tol = TRESHOLD)

def IsScaleApplied(Object: bpy.types.Object):
    return math.isclose(Object.scale[0], 1, abs_tol = TRESHOLD) and math.isclose(Object.scale[1], 1, abs_tol = TRESHOLD) and math.isclose(Object.scale[2], 1, abs_tol = TRESHOLD)

def IsRotationApplied(Object: bpy.types.Object):
    return math.isclose(Object.rotation_euler[0], 0, abs_tol = TRESHOLD) and math.isclose(Object.rotation_euler[1], 0, abs_tol = TRESHOLD) and math.isclose(Object.rotation_euler[2], 0, abs_tol = TRESHOLD)

def HasNGons(Object: bpy.types.Object):
    if Object.type != 'MESH':
        return False
    
    for p in Object.data.polygons:
        if len(p.vertices) > 4:
            return True

    return False

def FindPropID(Name: str):
    match = re.search("(hpr|pr|bg|vg)[0-9]*", Name)
    if not match:
        return False
    
    return True

def EqualSubDLevels(Object: bpy.types.Mesh):
    if len(Object.modifiers) <= 0:
        return True

    for m in Object.modifiers:
        if not m.type == 'SUBSURF':
            continue

        if m.render_levels != m.levels:
            return False

    return True

def FindPropCollection():
    for c in bpy.data.collections:
        if FindPropID(c.name_full):
            return c

    return None

def SetPropCollection(Collection):
    AssetChecker.PropCollectionOverride = Collection

def FindPropEmpty():
    # if not AssetChecker.PropCollection:
    #     return None
    
    for o in bpy.context.window_manager.PropCollectionOverride.objects:
        if not o.type == 'EMPTY' and not o.parent is None:
            continue
        
        return o
    
    return None

def UsesValidChars(Name: str):

    umlaut = 0
    for char in INVALID_CHARS:
        umlaut += Name.find(char)
    
    # no special char found
    if umlaut == (len(INVALID_CHARS) * -1):
        return True
    
    return False

def GetFilenameString():
    return bpy.data.filepath[bpy.data.filepath.rindex(OS_SEPARATOR) + 1: -6]

def IsParented(Object: bpy.types.Object, ToParent: bpy.types.Object):
    if Object.parent:
        if Object.parent != ToParent:
            IsParented(Object.parent, ToParent)
        else:
            return True
    else:
        return False

def SelectErrors(ErrorList: list):
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode = 'OBJECT')

    bpy.ops.object.select_all(action='DESELECT')

    for o in ErrorList:
        o.select_set(True)

    bpy.context.view_layer.objects.active = ErrorList[0]

class FTB_OT_PerformAssetCheck_Op(Operator):
    bl_idname = "utils.performassetcheck"
    bl_label = "Run Asset Check"
    bl_description = "Does Stuff"

    Checker = None

    @classmethod
    def poll(cls, context):
        wm = context.window_manager
        if not bpy.data.is_saved or bpy.data.filepath == "" or not wm.PropCollectionOverride or not wm.PropEmptyOverride :
            return False

        return True

    def execute(self, context):
        if not self.Checker:
            self.Checker = AssetChecker()

        wm = context.window_manager
        _propcollection = wm.PropCollectionOverride
        _propempty = wm.PropEmptyOverride 

        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode = 'OBJECT')

        bpy.ops.object.select_all(action='DESELECT')

        self.Checker.Initialize()

        _filename = GetFilenameString()
        #_propcollection = FindPropCollection()
        self.Checker.PropCollection = _propcollection

        AssetChecker.bFileIsClean = IsFileClean()

        AssetChecker.bFileInWorkspace = IsFileInWorkspace()
        AssetChecker.bPropIDFileName = FindPropID(_filename)
        AssetChecker.bProperFileName = UsesValidChars(_filename)

        if AssetChecker.PropCollection:
            #_propempty = FindPropEmpty()
            AssetChecker.PropEmpty = _propempty
            AssetChecker.bEqualFileCollectionName = (_filename == _propcollection.name_full)

            AssetChecker.bPropIDCollectionName = FindPropID(_propcollection.name_full)
            AssetChecker.bProperCollectionName = UsesValidChars(_propcollection.name_full)

            if AssetChecker.PropEmpty:
                AssetChecker.bEmptyOnWorldOrigin = IsOnWorldOrigin(_propempty)

                AssetChecker.bEqualFileEmptyName = (_filename == _propempty.name_full)
                AssetChecker.bEqualCollectonEmptyName = (_propcollection.name_full == _propempty.name_full)
                AssetChecker.bEqualNaming = AssetChecker.bEqualFileCollectionName and AssetChecker.bEqualCollectonEmptyName and AssetChecker.bEqualFileEmptyName

                AssetChecker.bPropIDEmptyName = FindPropID(_propempty.name_full)
                AssetChecker.bProperEmptyName = UsesValidChars(_propempty.name_full)

            for o in _propcollection.objects:              
                if o.type in ROGUE_OBJECTS:
                    AssetChecker.RogueObjectErrors.append(o)
                    continue

                if o.type in ['MESH', 'CURVE', 'SURFACE']:
                    
                    _bSubDError = False
                    _bDisplaceError = True
                    for m in o.modifiers:
                        if not m.type in ['SUBSURF', 'DISPLACE']:
                            continue

                        if m.type == 'SUBSURF':
                            if m.render_levels != m.levels:
                                _bSubDError = True
                        elif m.type == 'DISPLACE':
                            _bDisplaceError = False

                    if _bSubDError:
                        AssetChecker.SubDLevelErrors.append(o)
                    if _bDisplaceError:
                        AssetChecker.MissingDisplacementErrors.append(o)

                    if not IsScaleApplied(o):
                        AssetChecker.ApplyScaleErrors.append(o)

                    _usedmatslots = []
                    
                    #TODO: NGON Check curves, surfaces ?
                    if o.type in ['MESH']:
                        for f in o.data.polygons:
                            _usedmatslots.append(f.material_index)
                            if len(f.vertices) > 4:
                                AssetChecker.NGonErrors.append(o)    
                
                    if not o.material_slots:
                        AssetChecker.MissingSlotErrors.append(o)
                    else:
                        for i in range(len(o.material_slots)):
                            if o.material_slots[i].link != 'OBJECT':
                                AssetChecker.SlotLinkErrors.append(o)
                            if _usedmatslots.count(i) <= 0:
                                AssetChecker.UnusedSlotErrors.append(o)

                    if not IsParented(o, _propempty):
                        AssetChecker.ParentingErrors.append(o)

        # else:
        #     AssetChecker.bPropIDCollectionName = False
        #     AssetChecker.bProperCollectionName = False
        #     AssetChecker.bPropIDEmptyName = False
        #     AssetChecker.bProperEmptyName = False
        
        return {'FINISHED'}

class FTB_OT_DetectPropEmptyCollection_Op(Operator):
    bl_idname = "utils.detectpropemptycollection"
    bl_label = "Find Prop Empty & Collection"
    bl_description = "Does Stuff"
    
    @classmethod
    def poll(cls, context):
        if not bpy.data.is_saved or bpy.data.filepath == "":
            return False

        return True

    def execute(self, context):
        context.window_manager.PropCollectionOverride = FindPropCollection()
        context.window_manager.PropEmptyOverride = FindPropEmpty()
        return {'FINISHED'}

class FTB_OT_ShowRoguesError_Op(Operator):
    bl_idname = "object.showrogues"
    bl_label = "Select SubD Errors"
    bl_description = "Does Stuff"

    def execute(self, context):
        SelectErrors(AssetChecker.RogueObjectErrors)
        return {'FINISHED'}
        
class FTB_OT_ShowSubDErrors_Op(Operator):
    bl_idname = "object.showsubderror"
    bl_label = "Select SubD Errors"
    bl_description = "Does Stuff"

    def execute(self, context):
        SelectErrors(AssetChecker.SubDLevelErrors)
        #TODO: Select Modifier Panel
        return {'FINISHED'}

class FTB_OT_ShowDisplaceErrors_Op(Operator):
    bl_idname = "object.showdisplaceerror"
    bl_label = "Select SubD Errors"
    bl_description = "Does Stuff"

    def execute(self, context):
        SelectErrors(AssetChecker.MissingDisplacementErrors)
        #TODO: Select Modifier Panel
        return {'FINISHED'}

class FTB_OT_ShowScaleErrors_Op(Operator):
    bl_idname = "object.showscaleerror"
    bl_label = "Select SubD Errors"
    bl_description = "Does Stuff"

    def execute(self, context):
        SelectErrors(AssetChecker.ApplyScaleErrors)
        #TODO: Select Object Panel
        return {'FINISHED'}

class FTB_OT_ShowNGonErrors_Op(Operator):
    bl_idname = "object.showngonerror"
    bl_label = "Select SubD Errors"
    bl_description = "Does Stuff"

    def execute(self, context):
        SelectErrors(AssetChecker.NGonErrors)
        #TODO: Switch into edit mode and select ngons
        return {'FINISHED'}

class FTB_OT_ShowMissingSlotErrors_Op(Operator):
    bl_idname = "object.showmissingsloterror"
    bl_label = "Select SubD Errors"
    bl_description = "Does Stuff"

    def execute(self, context):
        SelectErrors(AssetChecker.MissingSlotErrors)
        #TODO: Select material Panel
        return {'FINISHED'}

class FTB_OT_ShowSlotLinkErrors_Op(Operator):
    bl_idname = "object.showslotlinkerror"
    bl_label = "Select SubD Errors"
    bl_description = "Does Stuff"

    def execute(self, context):
        SelectErrors(AssetChecker.SlotLinkErrors)
        #TODO: Select material Panel
        return {'FINISHED'}

class FTB_OT_ShowUnusedSlotErrors_Op(Operator):
    bl_idname = "object.showunusedsloterror"
    bl_label = "Select SubD Errors"
    bl_description = "Does Stuff"

    def execute(self, context):
        SelectErrors(AssetChecker.UnusedSlotErrors)
        #TODO: Select material Panel
        return {'FINISHED'}

class FTB_OT_ShowParentingErrors_Op(Operator):
    bl_idname = "object.showparentingerror"
    bl_label = "Select SubD Errors"
    bl_description = "Does Stuff"

    def execute(self, context):
        SelectErrors(AssetChecker.ParentingErrors)
        return {'FINISHED'}

class FTB_OT_ResolveFilenameError_Op(Operator):
    bl_idname = "wm.savefile"
    bl_label = "Select SubD Errors"
    bl_description = "Does Stuff"

    def execute(self, context):
        bpy.ops.wm.save_as_mainfile('INVOKE_AREA')

        return {'FINISHED'}

class FTB_OT_ResolveCollectionNameError_Op(Operator):
    bl_idname = "utils.changecollectionname"
    bl_label = "Enter valid Prop Collection Name"
    bl_description = "Does Stuff"

    #TODO: automatic name insert
    NewName: bpy.props.StringProperty(name="New Name: ", default = "")

    @classmethod
    def poll(cls, context):
        if AssetChecker.PropCollection:
             return True
        return False

    def execute(self, context):
        AssetChecker.PropCollection.name = self.NewName

        return {'FINISHED'}

    #TODO: validate user input
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class FTB_OT_Toggle_Face_Orient_Op(Operator):
    bl_idname = "view.toggle_face_orient"
    bl_label = "Toggle Face Orientation"
    bl_description = "Toggle the Face Orientation overlay"

    def execute(self, context):
        bpy.context.space_data.overlay.show_face_orientation = not(bpy.context.space_data.overlay.show_face_orientation)
        return {'FINISHED'}


class FTB_OT_SelectLocationNonZero_Op(Operator):
    bl_idname = "object.select_location_non_zero"
    bl_label = "Unapplied Location"
    bl_description = "Select all objects that have non-zero Location."
    bl_options = {"REGISTER", "UNDO"}

    # should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object

        if obj:
            if obj.mode == "OBJECT":
                return True

        return False

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        counter = 0

        for o in bpy.data.objects:
            if o.type in ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'LATTICE', 'EMPTY']:
                if o.location[0] != 0.0 or o.location[1] != 0.0 or o.location[2] != 0.0:
                    o.select_set(True)
                    counter += 1

        self.report({'INFO'}, str(counter) + " objects with non zero location")

        return {'FINISHED'}


class FTB_OT_SelectRotationNonZero_Op(Operator):
    bl_idname = "object.select_rotation_non_zero"
    bl_label = "Unapplied Rotation"
    bl_description = "Select all objects that have unapplied Rotation."
    bl_options = {"REGISTER", "UNDO"}

    # should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object

        if obj:
            if obj.mode == "OBJECT":
                return True

        return False

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        counter = 0

        for o in bpy.data.objects:
            if o.type in ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'LATTICE', 'EMPTY']:
                if o.rotation_euler[0] != 0.0 or o.rotation_euler[1] != 0.0 or o.rotation_euler[2] != 0.0:
                    o.select_set(True)
                    counter += 1

        self.report({'INFO'}, str(counter) +
                    " objects with unapplied rotation")

        return {'FINISHED'}


class FTB_OT_SelectScaleNonOne_Op(Operator):
    bl_idname = "object.select_scale_non_one"
    bl_label = "Unapplied Scale"
    bl_description = "Select all objects that do not have Scale of (1,1,1)"
    bl_options = {"REGISTER", "UNDO"}

    # should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object

        if obj:
            if obj.mode == "OBJECT":
                return True

        return False

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        counter = 0
        for o in bpy.data.objects:
            if o.type in ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'LATTICE', 'EMPTY']:
                if o.scale[0] != 1 or o.scale[1] != 1 or o.scale[2] != 1:
                    o.select_set(True)
                    counter += 1

        self.report({'INFO'}, str(counter) + " objects with unapplied scale")

        return {'FINISHED'}


class FTB_OT_SelectScaleNonUniform_Op(Operator):
    bl_idname = "object.select_scale_non_unform"
    bl_label = "Non Uniform Scale"
    bl_description = "Select all objects that do not have a uniform Scale (x=y=z))"
    bl_options = {"REGISTER", "UNDO"}

    # should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object

        if obj:
            if obj.mode == "OBJECT":
                return True

        return False

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        counter = 0
        for o in bpy.data.objects:
            if o.type in ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'LATTICE', 'EMPTY']:
                if o.type == 'MESH':
                    if not (o.scale[0] == o.scale[1] == o.scale[2]):
                        o.select_set(True)
                        counter += 1

        self.report({'INFO'}, str(counter) + " objects with non uniform scale")

        return {'FINISHED'}


class FTB_OT_SetToCenter_Op(Operator):
    bl_idname = "object.center_object"
    bl_label = "Center Object"
    bl_description = "Set the object to World Origin"
    bl_options = {"REGISTER", "UNDO"}

    # should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object

        if obj:
            if obj.mode == "OBJECT":
                return True

        return False

    def execute(self, context):
        offsetMode = bpy.context.tool_settings.transform_pivot_point
        bpy.ops.view3d.snap_cursor_to_center()
        bpy.context.tool_settings.transform_pivot_point = 'ACTIVE_ELEMENT'
        bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)
        bpy.context.tool_settings.transform_pivot_point = offsetMode
        return {'FINISHED'}


class FTB_OT_OriginToCursor_Op(Operator):
    bl_idname = "object.origin_to_cursor"
    bl_label = "Origin to cursor"
    bl_description = "Set object origin to 3D Cursor"
    bl_options = {"REGISTER", "UNDO"}

    # should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object

        if obj:
            if obj.mode == "OBJECT":
                return True

        return False

    def execute(self, context):
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        return {'FINISHED'}


class FTB_OT_CheckNgons_Op(Operator):
    bl_idname = "object.check_ngons"
    bl_label = "Check Ngons"
    bl_description = "Select all ngons of active object, if any"
    bl_options = {"REGISTER", "UNDO"}

    showPolys: BoolProperty(name="Show in Edit Mode")

    # should work in edit and object mode
    @classmethod
    def poll(cls, context):
        selection = context.selected_objects
        obj = context.active_object

        if selection:
            if not obj:
                return True

            elif obj and obj.mode == 'OBJECT':
                return True

            else:
                return False

        return False

    def execute(self, context):
        checkObjList = context.selected_objects
        ngonCount = 0
        objCount = 0
        objList = []

        bpy.ops.object.select_all(action='DESELECT')

        for obj in checkObjList:

            bpy.context.view_layer.objects.active = obj

            if obj.type != 'MESH':
                continue

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_face_by_sides(
                number=4, type='GREATER', extend=False)

            currentMesh = obj.data
            ngonCount += currentMesh.count_selected_items()[2]

            if (currentMesh.count_selected_items()[2] > 0):
                objCount += 1
                objList.append(obj)
                obj.select_set(True)

            bpy.ops.object.mode_set(mode='OBJECT')

        if objList:
            self.report({'WARNING'}, str(ngonCount) +
                        " Ngons found in " + str(objCount) + " Objects.")

            if self.showPolys:
                bpy.ops.object.mode_set(mode='EDIT')

        else:
            self.report({'INFO'}, "No Ngons found.")

        return {'FINISHED'}


class FTB_OT_ValidateMatSlots_Op(Operator):
    bl_idname = "object.validate_mat_slots"
    bl_label = "Validate Mat Slots"
    bl_description = "Validate if all objects have at least one material slot and if all material slots are stored on the object datablock"
    bl_options = {"REGISTER", "UNDO"}

    # should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object
        if not obj:
            return True

        if obj:
            if obj.mode == "OBJECT":
                return True

        return False

    def execute(self, context):

        objList = list()
        wm = bpy.context.window_manager

        if (wm.bActiveCollectionOnly):

            # Cancel if no active collection is found
            if not (bpy.context.collection):
                self.report({'ERROR'}, "No active collection")
                return {'CANCELLED'}

            # Limit validation to Meshes Curves and Surfaces
            for obj in bpy.context.collection.all_objects:
                if (obj.type in ['MESH', 'CURVE', 'SURFACE']):

                    # Report Object if it has no material slots and user has selected option in the interface
                    if (not obj.material_slots and wm.bIgnoreWithoutSlots == False):
                        objList.append(obj)

                    else:
                        for slot in obj.material_slots:
                            if slot.link == 'DATA':
                                objList.append(obj)

        else:
            # Limit validation to Meshes Curves and Surfaces
            for obj in bpy.context.view_layer.objects:
                if (obj.type in ['MESH', 'CURVE', 'SURFACE']):

                    # Report Object if it has no material slots and user has selected option in the interface
                    if (not obj.material_slots and wm.bIgnoreWithoutSlots == False):
                        objList.append(obj)

                    else:
                        for slot in obj.material_slots:
                            if slot.link == 'DATA':
                                objList.append(obj)

        if (objList):

            if (wm.bIgnoreWithoutSlots):
                self.report({'WARNING'}, "Found " + str(len(objList)) +
                            " Objects with incorrect material slots")

            if (not wm.bIgnoreWithoutSlots):
                self.report({'WARNING'}, "Found " + str(len(objList)) +
                            " Objects with incorrect or missing material slots")

            bpy.ops.object.select_all(action='DESELECT')

            if (wm.bActiveCollectionOnly):
                for obj in objList:

                    obj.select_set(True)

            else:
                for obj in objList:
                    obj.select_set(True)

        else:
            self.report({'INFO'}, "No invalid material slots found")

        return {'FINISHED'}


class FTB_OT_FindOrphanedObjects_Op(Operator):
    bl_idname = "object.find_orphaned_objects"
    bl_label = "Find Orphaned Objects"
    bl_description = "Find Objects that are not part of any View Layer or collection but are present in the .blend file"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):

        orphanList = list()

        for obj in bpy.data.objects:
            if (len(obj.users_collection) <= 0):
                orphanList.append(obj)

        if (orphanList):
            self.report({'WARNING'}, "Orphans found in File")
            ShowMessageBox("Please check Outliner to find Objects that are not part of the current View Layer",
                           "Orphaned objects found", 'ERROR')
            return self.execute(context)

        else:
            self.report({'INFO'}, "No orphans found")
            return {'FINISHED'}

    def execute(self, context):
        for area in bpy.context.screen.areas:
            if(area.type == 'OUTLINER'):
                outliner_space = area.spaces[0]
                outliner_space.display_mode = 'LIBRARIES'
        return {'FINISHED'}


def ShowMessageBox(message="", title="Message Box", icon='INFO'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


class FTB_OT_FindOrphanTextures_Op(Operator):
    bl_idname = "image.find_orphan_textures"
    bl_label = "Find Unused Textures"
    bl_description = "Check if there are any image data blocks in .blend-file with no users"
    bl_options = {"REGISTER", "UNDO"}

    # should only work in object mode
    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):

        orphanList = list()

        for img in bpy.data.images:
            if (img.users <= 0):
                orphanList.append(img)

        if (orphanList):
            self.report({'WARNING'}, "Orphan textures found in File")
            ShowMessageBox("Please check Outliner to find Images that are do not have any users",
                           "Orphaned objects found", 'ERROR')
            return self.execute(context)

        else:
            self.report({'INFO'}, "No unused textures")
            return {'FINISHED'}

    def execute(self, context):

        for area in bpy.context.screen.areas:
            if(area.type == 'OUTLINER'):
                outliner_space = area.spaces[0]
                outliner_space.display_mode = 'ORPHAN_DATA'

        return {'FINISHED'}

classes =   (
                FTB_OT_Toggle_Face_Orient_Op, FTB_OT_SelectScaleNonOne_Op, FTB_OT_SelectScaleNonUniform_Op,
                FTB_OT_SelectRotationNonZero_Op, FTB_OT_SelectLocationNonZero_Op, FTB_OT_SetToCenter_Op,
                FTB_OT_OriginToCursor_Op, FTB_OT_CheckNgons_Op, FTB_OT_ValidateMatSlots_Op,
                FTB_OT_FindOrphanedObjects_Op, FTB_OT_FindOrphanTextures_Op, FTB_OT_PerformAssetCheck_Op,
                FTB_OT_ShowSubDErrors_Op, FTB_OT_ShowRoguesError_Op, FTB_OT_ResolveFilenameError_Op,
                FTB_OT_ShowDisplaceErrors_Op, FTB_OT_ShowScaleErrors_Op, FTB_OT_ShowNGonErrors_Op,
                FTB_OT_ShowMissingSlotErrors_Op, FTB_OT_ShowSlotLinkErrors_Op, FTB_OT_ShowUnusedSlotErrors_Op,
                FTB_OT_ShowParentingErrors_Op, FTB_OT_ResolveCollectionNameError_Op, FTB_OT_DetectPropEmptyCollection_Op
            )


def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.app.handlers.depsgraph_update_pre.append(DepsgraphCustomUpdate)

def unregister():
    bpy.app.handlers.depsgraph_update_pre.remove(DepsgraphCustomUpdate)

    for c in reversed(classes):
        bpy.utils.unregister_class(c)
