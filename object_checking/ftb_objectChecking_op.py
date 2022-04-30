import math
import bpy

from bpy.app.handlers import persistent
from bpy.types import Operator
from .. utility_functions.ftb_string_utils import *
from . import Asset

TRESHOLD = 0.001
ROGUE_OBJECTS = ['CAMERA', 'LIGHT', 'GPENCIL', 'LIGHT', 'LIGHT_PROBE', 'SPEAKER', 'VOLUME', 'LIGHT_PROBE']

@persistent
def CustomLoadHandler(dummy):
    bpy.context.window_manager.PropCollectionReference = None
    bpy.context.window_manager.PropEmptyReference = None

@persistent
def DepsgraphCustomUpdate(self, context):
    pass

def IsFileClean():
    for o in bpy.data.objects:
        if o.users <= 0 or len(o.users_collection) <= 0:
            return False
    for i in bpy.data.images:
        if i.users <= 0:
            return False
    for m in bpy.data.materials:
        if m.users <= 0:
            return False
    return True

def IsOnWorldOrigin(Object: bpy.types.Object):
    return  math.isclose(Object.location[0], 0, abs_tol = TRESHOLD) and \
            math.isclose(Object.location[1], 0, abs_tol = TRESHOLD) and \
            math.isclose(Object.location[2], 0, abs_tol = TRESHOLD)

def IsScaleApplied(Object: bpy.types.Object):
    return  math.isclose(Object.scale[0], 1, abs_tol = TRESHOLD) and \
            math.isclose(Object.scale[1], 1, abs_tol = TRESHOLD) and \
            math.isclose(Object.scale[2], 1, abs_tol = TRESHOLD)

def IsRotationApplied(Object: bpy.types.Object):
    return  math.isclose(Object.rotation_euler[0], 0, abs_tol = TRESHOLD) and \
            math.isclose(Object.rotation_euler[1], 0, abs_tol = TRESHOLD) and \
            math.isclose(Object.rotation_euler[2], 0, abs_tol = TRESHOLD)

def FindPropCollection():
    # collect valid finds
    result = []
    for c in bpy.data.collections:
        if c.library or c.override_library: #skip linked collections
            continue

        value = 0
        if c.name_full.find("fs") == 0:
            value += 1
        if ContainsPropID(c.name_full):
            value += 2
        if value > 0:
            result.append([value, c])
    #determine best find
    if result:
        result.sort(reverse = True, key = lambda row: (row[0]))
        return result[0][1]

    return None

def FindPropEmpty():
    if not bpy.context.window_manager.PropCollectionReference:
        return None

    # collect valid finds
    result = []
    for o in bpy.context.window_manager.PropCollectionReference.objects:
        if not Asset.IsPropEmpty(o): #skip linked empties and instanced objects, fields, etc
            continue

        if o.type == 'EMPTY' and o.parent is None and o.children:
            value = 0
            if o.name_full.find("fs") == 0:
                value += 1
            if ContainsPropID(o.name_full):
                value += 2

            result.append([value, o])
    #determine best find
    if result:
        result.sort(reverse = True, key = lambda row: (row[0]))
        return result[0][1]
    
    return None

def IsParentedToRoot(Object: bpy.types.Object, Root: bpy.types.Object):
    if Object.parent:
        if Object.parent != Root:
            return IsParentedToRoot(Object.parent, Root)
        else:
            return True
    else:
        return False

def SelectErrors(ErrorList: list):
    if not ErrorList:
        return

    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode = 'OBJECT')

    bpy.ops.object.select_all(action='DESELECT')

    for o in ErrorList:
        if o.hide_get():
            o.hide_set(False)
        if o.hide_viewport:
            o.hide_viewport = False

        o.select_set(True)

    bpy.context.view_layer.objects.active = ErrorList[0]
    bpy.ops.view3d.view_selected(use_all_regions=True)

def SelectPropertiesPanel(PanelEnum: str):
    for area in bpy.context.screen.areas:
        if(area.type == 'PROPERTIES'):
            try:
                area.spaces[0].context = PanelEnum 
            except:
                pass

def SuggestValidName():
    wm = bpy.context.window_manager
    filename = GetFilenameString()
    collectionName: str = ""
    emptyName: str = ""
    if wm.PropCollectionReference:
        collectionName = wm.PropCollectionReference.name_full
    if wm.PropEmptyReference:
        emptyName = wm.PropEmptyReference.name_full

    if filename.find("fs_") == 0 and ContainsPropID(filename):
        filename = ReplaceInvalidChars(filename)
        return filename
    elif collectionName.find("fs_") == 0 and ContainsPropID(collectionName):
        collectionName = ReplaceInvalidChars(collectionName)
        return collectionName
    elif emptyName.find("fs_") == 0 and ContainsPropID(emptyName):
        emptyName = ReplaceInvalidChars(emptyName)
        return emptyName
    else:
        return "fs_pr00000_"

class FTB_OT_PerformAssetCheck_Op(Operator):
    bl_idname = "utils.perform_asset_check"
    bl_label = "Run Asset Check"
    bl_description = "Runs various checks based on the prop empty, prop collection and its containing objects selected above"

    @classmethod
    def poll(cls, context):
        wm = context.window_manager
        if not Asset.IsSaved():
            cls.poll_message_set("File must be saved to use this feature")
            return False

        if not(wm.PropCollectionReference and wm.PropEmptyReference):
            cls.poll_message_set("Missing Prop Collection and/or Prop Empty Object")
            return False

        if wm.PropEmptyReference.type != 'EMPTY':
            cls.poll_message_set("The Prop Empty Object is not of Type 'EMPTY'")
            return False

        return True

    def execute(self, context):

        def ObjectCheckingRoutine(Collection: bpy.types.Collection):
            """
            FTB_OT_PerformAssetCheck_Op - Internal method that loops over all objects inside the collection to check for errors. Nessesary to call it recursivly
            param Collection: Checks all objects found inside the passed collection argument
            """
            for c in Collection.children:
                ObjectCheckingRoutine(c)

            for o in Collection.objects:
                if o.type in ROGUE_OBJECTS or o.library or o.override_library:
                    Asset.RogueObjectErrors.append(o)
                    continue
                if o.instance_collection:
                    if o.instance_collection.library:
                        Asset.RogueObjectErrors.append(o)
                        continue

                if not IsRotationApplied(o):
                    Asset.ApplyRotNotification.append(o)

                if UsesInvalidChars(o.name_full):
                    Asset.InvalidNameErrors.append(o)

                if not IsScaleApplied(o):
                    Asset.ApplyScaleErrors.append(o)

                if o.type in ['MESH', 'CURVE', 'SURFACE', 'FONT', 'LATTICE']:
                    if not o.data.shape_keys:
                        Asset.MissingShapeKeysNotification.append(o)

                    _bSubDError = False
                    _bDisplaceError = False
                    _bDisplaceNotify = True
                    for m in o.modifiers:
                        if not m.type in ['SUBSURF', 'DISPLACE']:
                            continue
                        
                        if m.type == 'SUBSURF':
                            if m.render_levels != m.levels:
                                _bSubDError = True
                        elif m.type == 'DISPLACE':
                            _bDisplaceNotify = False
                            if not(m.texture and m.direction in ['X', 'Y', 'Z', 'RGB_TO_XYZ']):
                                _bDisplaceError = True

                    if _bSubDError and o.type != 'LATTICE':
                        Asset.SubDLevelErrors.append(o)
                    if _bDisplaceError and o.type == 'MESH':
                        Asset.DisplacementErrors.append(o)
                    if _bDisplaceNotify and o.type == 'MESH':
                        Asset.MissingDisplacementNotification.append(o)    

                    _usedmatslots = []
                    if o.type == 'MESH':
                        for p in o.data.polygons:
                            _usedmatslots.append(p.material_index) # not part of ngon check                     
                            # collects polies mat index since we are looping over all polies anyways
                            # used later to check for unused material slots
                            
                            # ngon check
                            if len(p.vertices) > 4:
                                Asset.NGonErrors.append(o)
                                break 
                    
                    if o.type != 'LATTICE':
                        if not o.material_slots:
                            Asset.MissingSlotErrors.append(o)
                        else:
                            for i in range(len(o.material_slots)):
                                if o.material_slots[i].link != 'OBJECT':
                                    Asset.SlotLinkErrors.append(o)
                                if _usedmatslots and _usedmatslots.count(i) <= 0:
                                    Asset.UnusedSlotErrors.append(o)

                if not IsParentedToRoot(o, propEmpty) and o != propEmpty:
                    Asset.ParentingErrors.append(o)
                    
        if not Asset.bChecked:
            Asset.bChecked = True

        Asset.InitializeCheck(Asset)
        wm = context.window_manager
        propCollection = wm.PropCollectionReference
        propEmpty = wm.PropEmptyReference
        wm.bNormalsButtonClicked = False
        wm.bNormalsChecked = False
        context.space_data.overlay.show_face_orientation = False

        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode = 'OBJECT')

        bpy.ops.object.select_all(action='DESELECT')

        _filename = GetFilenameString()

        Asset.bFileIsClean = IsFileClean()

        Asset.bPropIDFileName = ContainsPropID(_filename)
        Asset.bProperFileName = not UsesInvalidChars(_filename)

        if propCollection:
            Asset.bEqualFileCollectionName = (_filename == propCollection.name_full)

            Asset.bPropIDCollectionName = ContainsPropID(propCollection.name_full)
            Asset.bProperCollectionName = not UsesInvalidChars(propCollection.name_full)

            if propEmpty:
                Asset.bEmptyOnWorldOrigin = IsOnWorldOrigin(propEmpty)

                Asset.bEqualFileEmptyName = (_filename == propEmpty.name_full)
                Asset.bEqualCollectonEmptyName = (propCollection.name_full == propEmpty.name_full)
                Asset.bEqualNaming = Asset.bEqualFileCollectionName and Asset.bEqualCollectonEmptyName and Asset.bEqualFileEmptyName

                Asset.bPropIDEmptyName = ContainsPropID(propEmpty.name_full)
                Asset.bProperEmptyName = not UsesInvalidChars(propEmpty.name_full)

            ObjectCheckingRoutine(propCollection)
        
        return {'FINISHED'}

class FTB_OT_DetectPropEmptyCollection_Op(Operator):
    bl_idname = "utils.detect_prop_empty_collection"
    bl_label = "Find Prop Empty & Collection"
    bl_description = "Tries to find the blend files prop empty and prop collection. If it can't find both or one of them," + \
                    "there is a high chance that something is not right with your prop empty and/or collection"

    def execute(self, context):
        context.window_manager.PropCollectionReference = FindPropCollection()
        context.window_manager.PropEmptyReference = FindPropEmpty()
        return {'FINISHED'}

class FTB_OT_ShowNameError_Op(Operator):
    bl_idname = "object.show_name_error"
    bl_label = "Invalid Name"

    @classmethod
    def description(cls, context, properties):
        charStr = str(list(INVALID_CHARS))
        for c in "'[]":
            charStr = charStr.replace(c, "")
        return "Selects all objects with names containing unwanted characters. Please rename objects containing the following unwanted characters:\n" + \
                charStr

    @classmethod
    def poll(cls, context):
        if not Asset.InvalidNameErrors:
            return False
        return True

    def execute(self, context):
        SelectErrors(Asset.InvalidNameErrors)
        SelectPropertiesPanel('OBJECT') 
        return {'FINISHED'}

class FTB_OT_ShowRoguesError_Op(Operator):
    bl_idname = "object.show_rogues"
    bl_label = "Invalid Object"

    @classmethod
    def description(cls, context, properties):
        objList = ROGUE_OBJECTS
        objList.insert(0,'LINKED OBJECTS')
        objStr = str(list(objList))
        for c in "'[]":
            objStr = objStr.replace(c, "")
        return "Selects all unwanted objects inside Prop Collection. Please move objects out of prop collection. Unwanted objects are the following:\n" + objStr

    @classmethod
    def poll(cls, context):
        if not Asset.RogueObjectErrors:
            return False
        return True

    def execute(self, context):
        SelectErrors(Asset.RogueObjectErrors)
        return {'FINISHED'}
        
class FTB_OT_ShowSubDErrors_Op(Operator):
    bl_idname = "object.show_subd_error"
    bl_label = "Select SubD Errors"
    bl_description = "Shows all objects with Subdivision modifiers where viewport and render subdivision levels are not equal. Please equalize the levels"

    @classmethod
    def poll(cls, context):
        if not Asset.SubDLevelErrors:
            return False
        return True

    def execute(self, context):
        SelectErrors(Asset.SubDLevelErrors)
        SelectPropertiesPanel('MODIFIER')
        return {'FINISHED'}

class FTB_OT_ShowDisplaceErrors_Op(Operator):
    bl_idname = "object.show_displace_error"
    bl_label = "Displacement Error"
    bl_description = "Shows all objects with displacement modifiers without a valid texture or wrong direction settings"

    @classmethod
    def poll(cls, context):
        if not Asset.DisplacementErrors:
            return False
        return True

    def execute(self, context):
        SelectErrors(Asset.DisplacementErrors)
        SelectPropertiesPanel('MODIFIER') 
        return {'FINISHED'}

class FTB_OT_ShowScaleErrors_Op(Operator):
    bl_idname = "object.show_scale_error"
    bl_label = "Apply Scale Error"
    bl_description = "Shows all objects with unapplied scale. Scale must be applied to have 1.0 on all axis"

    @classmethod
    def poll(cls, context):
        if not Asset.ApplyScaleErrors:
            return False
        return True

    def execute(self, context):
        SelectErrors(Asset.ApplyScaleErrors)
        SelectPropertiesPanel('OBJECT') 
        return {'FINISHED'}

class FTB_OT_ShowNGonErrors_Op(Operator):
    bl_idname = "object.show_ngon_error"
    bl_label = "NGon Error"
    bl_description = "Shows all meshes that have polygons with more than 4 vertices. Please remove NGons by resolving them to quads or tris"

    @classmethod
    def poll(cls, context):
        if not Asset.NGonErrors:
            return False
        return True

    def execute(self, context):
        SelectErrors(Asset.NGonErrors)
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_face_by_sides(number=4, type='GREATER', extend=False)
        return {'FINISHED'}

class FTB_OT_ShowMissingSlotErrors_Op(Operator):
    bl_idname = "object.show_missing_slot_error"
    bl_label = "Missing Material Slot"
    bl_description = "Shows all objects that do not have a material slot. Please add at least one"

    @classmethod
    def poll(cls, context):
        if not Asset.MissingSlotErrors:
            return False
        return True

    def execute(self, context):
        SelectErrors(Asset.MissingSlotErrors)
        SelectPropertiesPanel('MATERIAL')
        return {'FINISHED'}

class FTB_OT_ShowSlotLinkErrors_Op(Operator):
    bl_idname = "object.show_slot_link_error"
    bl_label = "Material Link Error"
    bl_description = "Shows all objects with material links not set to 'OBJECT'. Please change all slots with wrong linking"

    @classmethod
    def poll(cls, context):
        if not Asset.SlotLinkErrors:
            return False
        return True

    def execute(self, context):
        SelectErrors(Asset.SlotLinkErrors)
        SelectPropertiesPanel('MATERIAL')
        return {'FINISHED'}

class FTB_OT_ShowUnusedSlotErrors_Op(Operator):
    bl_idname = "object.show_unused_slot_error"
    bl_label = "Unusued Material Slot"
    bl_description = "Shows all objects with at least one material slot that does not have any faces assigned to it. Please either delete the slot or assign faces to it"

    @classmethod
    def poll(cls, context):
        if not Asset.UnusedSlotErrors:
            return False
        return True

    def execute(self, context):
        SelectErrors(Asset.UnusedSlotErrors)
        SelectPropertiesPanel('MATERIAL')
        return {'FINISHED'}

class FTB_OT_ShowParentingErrors_Op(Operator):
    bl_idname = "object.show_parenting_error"
    bl_label = "Parenting Error"
    bl_description = "Shows all objects that are not parented to the prop empty. All objects inside the prop collection must be parented to the prop empty"

    @classmethod
    def poll(cls, context):
        if not Asset.ParentingErrors:
            return False
        return True

    def execute(self, context):
        SelectErrors(Asset.ParentingErrors)
        return {'FINISHED'}

class FTB_OT_ShowApplyRotNotification_Op(Operator):
    bl_idname = "object.show_apply_rot_notification"
    bl_label = "Unapplied Rotation"
    bl_description = "Shows objects with unapplied rotation. This is just a notification. Fixing this is optional"

    @classmethod
    def poll(cls, context):
        if not Asset.ApplyRotNotification:
            return False
        return True

    def execute(self, context):
        SelectErrors(Asset.ApplyRotNotification)
        SelectPropertiesPanel('OBJECT')
        return {'FINISHED'}

class FTB_OT_ShowDisplaceNotification_Op(Operator):
    bl_idname = "object.show_displace_notify"
    bl_label = "Select SubD Errors"
    bl_description = "Shows meshes without displacement modifier. This is just a notification. Fixing this is optional"

    @classmethod
    def poll(cls, context):
        if not Asset.MissingDisplacementNotification:
            return False
        return True

    def execute(self, context):
        SelectErrors(Asset.MissingDisplacementNotification)
        SelectPropertiesPanel('MODIFIER') 
        return {'FINISHED'}

class FTB_OT_ShowShapeKeyNotification_Op(Operator):
    bl_idname = "object.show_shape_key_notification"
    bl_label = "Select SubD Errors"
    bl_description = "Shows objects missing shape keys. This is just a notification. Fixing this is optional"

    @classmethod
    def poll(cls, context):
        if not Asset.MissingShapeKeysNotification:
            return False
        return True

    def execute(self, context):
        SelectErrors(Asset.MissingShapeKeysNotification)
        SelectPropertiesPanel('DATA')
        return {'FINISHED'}

class FTB_OT_ResolveFilenameError_Op(Operator):
    bl_idname = "wm.save_file"
    bl_label = "Save File"
    bl_description = "Opens file dialog to save file to workspace with correct name"

    def execute(self, context):
        bpy.ops.wm.save_as_mainfile('INVOKE_AREA')
        return {'FINISHED'}

class FTB_OT_ResolveCollectionNameError_Op(Operator):
    bl_idname = "utils.change_collection_name"
    bl_label = "Enter valid Prop Collection Name"
    bl_description = "Opens dialog to rename the prop collection"

    NewName: bpy.props.StringProperty(name="New Name", default = "")

    def invoke(self, context, event):
        self.NewName = SuggestValidName()
        return context.window_manager.invoke_props_dialog(self, width = 500)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.alert = True
        col.label(text = "WARNING!")
        col.label(text = "Renaming an the prop collection of an already linked prop will destroy its link in all sets.")
        col.label(text = "If prop is already in production, please make sure to fix all broken links after this operation")
        col.label(text = "Alternativly, don't rename it and ignore the error")
        col.alert = False
        #TODO: validate user input
        # Validation works inside draw() but there is no update callback while typing into the text box, 
        # thus no reliable user feedback
        ######
        # if self.NewName.find("fs_") != 0:
        #     col.alert = True
        #     col.label(text = "MISSING FS")
        #     col.alert = False
        row = col.row()
        row.alignment = 'LEFT'
        split = row.split(factor = 0.31)
        split.label(text = "Old Name: ")
        split.label(text = context.window_manager.PropCollectionReference.name_full)
        col.prop(self, "NewName", expand = True)

    @classmethod
    def poll(cls, context):
        if context.window_manager.PropCollectionReference:
             return True
        return False

    def execute(self, context):
        context.window_manager.PropCollectionReference.name = self.NewName
        return {'FINISHED'}

class FTB_OT_ResolveEmptyNameError_Op(Operator):
    bl_idname = "utils.changeemptyname"
    bl_label = "Enter valid Prop Empty Name"
    bl_description = "Opens dialog to rename the prop empty"

    NewName: bpy.props.StringProperty(name="New Name", default = "")

    def invoke(self, context, event):
        self.NewName = SuggestValidName()
        return context.window_manager.invoke_props_dialog(self, width = 500)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.alert = True
        col.label(text = "WARNING!")
        col.label(text = "Renaming an the empty of an already linked prop will destroy its link in all sets.")
        col.label(text = "If prop is already in production, please make sure to fix all broken links after this operation")
        col.label(text = "Alternativly, don't rename it and ignore the error")
        col.alert = False
        #TODO: validate user input
        # Validation works inside draw() but there is no update callback while typing into text box, 
        # thus no reliable user feedback
        ######
        # if self.NewName.find("fs_") != 0:
        #     col.alert = True
        #     col.label(text = "MISSING FS")
        #     col.alert = False
        row = col.row()
        row.alignment = 'LEFT'
        split = row.split(factor = 0.31)
        split.label(text = "Old Name: ")
        split.label(text = context.window_manager.PropCollectionReference.name_full)
        col.prop(self, "NewName", expand = True)

    @classmethod
    def poll(cls, context):
        if context.window_manager.PropEmptyReference:
             return True
        return False

    def execute(self, context):
        context.window_manager.PropEmptyReference.name = self.NewName
        return {'FINISHED'}

class FTB_OT_CleanFile_Op(Operator):
    bl_idname = "utils.clean_file"
    bl_label = "Clean File"
    bl_description = "Removes orphaned data and objects. Might not be able to catch everything. Manual clean up may be necessary"

    def execute(self, context):
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        self.report({'INFO'}, "Removed orphan data")
        return {'FINISHED'}

class FTB_OT_MoveEmptyToOrigin_Op(Operator):
    bl_idname = "object.move_empty_to_origin"
    bl_label = "Move to Origin"
    bl_description = "Moves prop empty to world origin"

    @classmethod
    def poll(cls, context):
        if not context.window_manager.PropEmptyReference:
            return False
        if IsOnWorldOrigin(context.window_manager.PropEmptyReference):
            return False
        return True

    def execute(self, context):
        empty = context.window_manager.PropEmptyReference
        empty.location =(0,0,0)
        return {'FINISHED'}

class FTB_OT_Toggle_Face_Orient_Op(Operator):
    bl_idname = "view.toggle_face_orient"
    bl_label = "Toggle Face Orientation"
    bl_description = "Toggle normals overlay. All normals facing outwards need to be blue. Red is usually not good if mesh is double sided. Please flip normals to correct the facing direction"

    def execute(self, context):
        context.window_manager.bNormalsButtonClicked = True
        context.space_data.overlay.show_face_orientation = not(context.space_data.overlay.show_face_orientation)
        return {'FINISHED'}

classes =   (
                FTB_OT_Toggle_Face_Orient_Op,
                FTB_OT_PerformAssetCheck_Op, FTB_OT_ShowSubDErrors_Op, FTB_OT_ShowRoguesError_Op, 
                FTB_OT_ResolveFilenameError_Op, FTB_OT_ShowDisplaceErrors_Op, FTB_OT_ShowScaleErrors_Op, 
                FTB_OT_ShowNGonErrors_Op, FTB_OT_ShowMissingSlotErrors_Op, FTB_OT_ShowSlotLinkErrors_Op, 
                FTB_OT_ShowUnusedSlotErrors_Op, FTB_OT_ShowParentingErrors_Op, FTB_OT_ResolveCollectionNameError_Op, 
                FTB_OT_DetectPropEmptyCollection_Op, FTB_OT_ShowApplyRotNotification_Op, FTB_OT_ShowShapeKeyNotification_Op, 
                FTB_OT_ResolveEmptyNameError_Op, FTB_OT_ShowNameError_Op, FTB_OT_CleanFile_Op, FTB_OT_ShowDisplaceNotification_Op,
                FTB_OT_MoveEmptyToOrigin_Op
            )

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.app.handlers.load_pre.append(CustomLoadHandler)
    bpy.app.handlers.depsgraph_update_post.append(DepsgraphCustomUpdate)

def unregister():
    bpy.app.handlers.depsgraph_update_post.remove(DepsgraphCustomUpdate)
    bpy.app.handlers.load_pre.remove(CustomLoadHandler)
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
