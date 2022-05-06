
import bpy

from bpy.types import Operator
from bpy.app.handlers import persistent

from .. utility_functions.ftb_transform_utils import ob_Copy_Vis_Loc
from .. utility_functions.ftb_transform_utils import ob_Copy_Vis_Rot
from .. utility_functions.ftb_transform_utils import ob_Copy_Vis_Sca
from .. utility_functions.ftb_string_utils import strip_End_Numbers


@persistent
def UpdateLayerID(self, context):
    wm = bpy.context.window_manager
    wm.MaskLayerID = BinToDec(bpy.context.collection.lineart_intersection_mask)


def DecToBin(n, OutBinaryArray):
    if not n == 0:
        OutBinaryArray.append(n % 2)
        DecToBin(n >> 1, OutBinaryArray)


def BinToDec(BinaryArray):
    n = 0
    for i in reversed(range(len(BinaryArray))):
        n += BinaryArray[i] * pow(2, i)
    return n


def ConvertLayerIDToMask(self, context):
    Collection = context.collection
    LayerID = context.window_manager.MaskLayerID

    Mask = []
    DecToBin((LayerID % 256), Mask)
    for i in range(len(Mask), 8):
        Mask.append(0)

    for i in range(0, len(Collection.lineart_intersection_mask)):
        Collection.lineart_intersection_mask[i] = Mask[i]


def ModifyCollectionLineArtMask(Collection, Mask):
    Collection.lineart_use_intersection_mask = Mask[0]
    for i in range(0, len(Collection.lineart_intersection_mask)):
        Collection.lineart_intersection_mask[i] = Mask[(i+1) % 9]


def PropagateCollectionMaskSettings(Collection, Mask, bForAllChildren=False):

    if Collection.children:
        for c in Collection.children:
            ModifyCollectionLineArtMask(c, Mask)
            if bForAllChildren:
                PropagateCollectionMaskSettings(c, Mask, bForAllChildren)


def GetMaskSettings(FromCollection):
    Mask = [0]*9

    Mask[0] = FromCollection.lineart_use_intersection_mask
    for i in range(0, len(FromCollection.lineart_intersection_mask)):
        Mask[(i+1) % 9] = FromCollection.lineart_intersection_mask[i]

    return Mask


def drawLineArtMaskButton(self, context):
    wm = context.window_manager

    ButtonLabel = "Propagate to all children"
    if not wm.bForAllChildren:
        ButtonLabel = "Propagate to immediate children"

    layout = self.layout
    col = layout.column()
    col.alignment = 'RIGHT'
    col.prop(wm, "MaskLayerID", text="Layer")
    col.separator()

    row = col.row(align=True)
    row.operator("collection.propagatelineartmask", text=ButtonLabel)
    row.prop(wm, "bForAllChildren", text="", icon='OUTLINER_OB_GROUP_INSTANCE')

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

class FTB_OT_CopyLocation_Op(Operator):
    bl_idname = "object.copy_location"
    bl_label = "Copy Location"
    bl_description = "Copy location from active object to selected"
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

        sourceObj = bpy.context.active_object

        for obj in bpy.context.selected_objects:
            ob_Copy_Vis_Loc(obj, sourceObj)
        return {'FINISHED'}


class FTB_OT_CopyRotation_Op(Operator):
    bl_idname = "object.copy_rotation"
    bl_label = "Copy Rotation"
    bl_description = "Copy rotation from active object to selected"
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

        sourceObj = bpy.context.active_object

        for obj in bpy.context.selected_objects:
            ob_Copy_Vis_Rot(obj, sourceObj)
        return {'FINISHED'}


class FTB_OT_CopyScale_Op(Operator):
    bl_idname = "object.copy_scale"
    bl_label = "Copy Scale"
    bl_description = "Copy scale from active object to selected"
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

        sourceObj = bpy.context.active_object

        for obj in bpy.context.selected_objects:
            ob_Copy_Vis_Sca(obj, sourceObj)
        return {'FINISHED'}


class FTB_OT_OverrideRetainTransform_Op(Operator):
    bl_idname = "object.override_retain_transform"
    bl_label = "Override Keep Transform"
    bl_description = "Make a library override and retain the transform of the previous instance object"
    bl_options = {"REGISTER", "UNDO"}

    # should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object

        if obj:
            if obj.mode == "OBJECT" and obj.type == 'EMPTY' and obj.is_instancer:
                return True
        return False

    def execute(self, context):
        objName = context.active_object.name
        objLoc = context.active_object.location
        objRot = context.active_object.rotation_euler
        objScale = context.active_object.scale

        # add new empty object to temporarily store transform and parent matrix of linked object
        tempOb = bpy.data.objects.new(objName + "phx", None)
        bpy.context.scene.collection.objects.link(tempOb)

        # tempOb copy transform from linked object
        ob_Copy_Vis_Loc(tempOb, context.active_object)
        ob_Copy_Vis_Rot(tempOb, context.active_object)
        ob_Copy_Vis_Sca(tempOb, context.active_object)

        # rename the linked object before overriding, so the objects created by
        # library override can have the same name as the original linked object had
        bpy.context.active_object.name = objName + "phName"

        bpy.ops.object.make_override_library()
        newOb = bpy.data.collections[strip_End_Numbers(
            objName)].objects[strip_End_Numbers(objName)]

        ob_Copy_Vis_Loc(newOb, tempOb)
        ob_Copy_Vis_Rot(newOb, tempOb)
        ob_Copy_Vis_Sca(newOb, tempOb)

        bpy.data.objects.remove(tempOb, do_unlink=True)

        return {'FINISHED'}

    def invoke(self, context, event):
        return bpy.context.window_manager.invoke_confirm(self, event)


class FTB_OT_CollectionNameToMaterial_Op(Operator):
    bl_idname = "object.collection_name_to_material"
    bl_label = "Collection Name To Material"
    bl_description = "Name the active Material the same as the active Collection"
    bl_options = {"REGISTER", "UNDO"}

    # should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object

        if obj:
            if obj.mode == "OBJECT" and obj.type == 'MESH':
                return True
        return False

    def execute(self, context):
        bpy.context.active_object.active_material.name = bpy.context.collection.name
        return {'FINISHED'}


class FTB_OT_ObjectNameToMaterial_Op(Operator):
    bl_idname = "object.object_name_to_material"
    bl_label = "Object Name To Material"
    bl_description = "Name the active Material the same as the active Object"
    bl_options = {"REGISTER", "UNDO"}

    # should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object

        if obj:
            if obj.mode == "OBJECT" and obj.type == 'MESH':
                return True
        return False

    def execute(self, context):
        bpy.context.active_object.active_material.name = bpy.context.active_object.name
        return {'FINISHED'}


class FTB_OT_SetLineartSettings_Op(Operator):
    bl_idname = "object.set_lineart_settings"
    bl_label = "Set Line Settings"
    bl_description = "Change Lineart usage for all selected objects at once"
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
        for obj in bpy.context.selected_objects:
            obj.lineart.usage = bpy.context.window_manager.lineUsage
        return {'FINISHED'}

    def invoke(self, context, event):
        return bpy.context.window_manager.invoke_confirm(self, event)


class FTB_OT_SetMatLinks_Op(Operator):
    bl_idname = "object.set_material_links"
    bl_label = "Set Material Links"
    bl_description = "Set Material Slot links for selected objects"
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

    def changeMatLinks(self, prop_collection):
        wm = bpy.context.window_manager
        for obj in prop_collection:
            if (obj.type in ['MESH', 'CURVE', 'SURFACE']):

                # Case link = Object
                if (wm.matSlotLink == 'OBJECT'):
                    for slot in obj.material_slots:
                        slot.link = 'OBJECT'

                # Case link = Data
                elif (wm.matSlotLink == 'DATA'):
                    for slot in obj.material_slots:
                        slot.link = 'DATA'

    def execute(self, context):
        wm = bpy.context.window_manager

        # Case limit = View Layer
        if (wm.matSlotLinkLimit == 'VIEW_LAYER'):
            if (not bpy.context.view_layer.objects):
                self.report(
                    {'ERROR'}, "No valid objects found in current view layer")
                return {'CANCELLED'}
            else:
                self.changeMatLinks(bpy.context.view_layer.objects)
                self.report({'INFO'}, "Material slots linked to " +
                            wm.matSlotLink + " for view layer.")

        # Case limit = Active Collection
        if (wm.matSlotLinkLimit == 'COLLECTION'):
            if (not bpy.context.collection):
                self.report({'ERROR'}, "No active collection")
                return {'CANCELLED'}

            else:
                self.changeMatLinks(bpy.context.collection.objects)
                self.report({'INFO'}, "Material slots linked to " +
                            wm.matSlotLink + " for active collection.")

        # Case limit = Current Selection
        if (wm.matSlotLinkLimit == 'SELECTION'):
            if (not bpy.context.selected_objects):
                self.report({'ERROR'}, "No objects selected")

            else:
                self.changeMatLinks(bpy.context.selected_objects)
                self.report({'INFO'}, "Material slots linked to " +
                            wm.matSlotLink + " for selected objects.")

        return {'FINISHED'}

    def invoke(self, context, event):
        return bpy.context.window_manager.invoke_confirm(self, event)


class FTB_OT_ClearMaterialSlots_Op(Operator):
    bl_idname = "object.clear_material_slots"
    bl_label = "Clear Material Slots"
    bl_description = "Clears all material slots by setting it to None"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def description(cls, context, properties):
        wm = context.window_manager
        selection = wm.matSlotLinkLimit

        desc = "Clears all material slots on objects"
        if selection == 'VIEW_LAYER':
            desc = "Clears all material slots on visible objects in view layer"
        elif selection == 'COLLECTION':
            desc = "Clears all material slots on objects in active collection"
        elif selection == 'SELECTION':
            desc = "Clears all material slots on selected objects"

        return desc

    def execute(self, context):
        wm = context.window_manager
        selection = wm.matSlotLinkLimit
        objects = []

        if selection == 'VIEW_LAYER':
            objects = context.view_layer.objects
        elif selection == 'COLLECTION':
            objects = context.collection.objects
        elif selection == 'SELECTION':
            objects = context.view_layer.objects.selected

        if not objects:
            self.report({'WARNING'}, "No objects in active selection. Operation cancelled")
            return {'CANCELLED'}

        objCount = 0
        slotCount = 0
        for obj in objects:
            if obj.override_library or len(obj.material_slots) <= 0:
                continue
            
            objCount += 1
            for slot in obj.material_slots:
                if slot.material == None:
                    continue

                slot.material = None
                slotCount += 1

        if objCount == 0:
            self.report({'INFO'}, "Operation Finished. No objects with editable slots in selection.")
            return {'CANCELLED'}
        elif slotCount == 0:
            self.report({'INFO'}, "Operation Finished. All slots in selection are already cleared.")
            return {'CANCELLED'}
        else:
            self.report({'INFO'}, "Operation Finished. Successfully cleared " + str(slotCount) + " slots on " + str(objCount) + " objects.")

        return {'FINISHED'}

class FTB_OT_PropagateLineArtMaskSettings_Op(Operator):

    bpy.types.WindowManager.bForAllChildren = bpy.props.BoolProperty(
        default=True)
    bpy.types.WindowManager.MaskLayerID = bpy.props.IntProperty(
        min=0, max=255, update=ConvertLayerIDToMask)

    bl_idname = "collection.propagatelineartmask"
    bl_label = "Propagate to child collections"
    bl_description = "Copies the Line Art Mask settings from this collection to all its children or its immediate children."
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        collection = context.collection
        mask = GetMaskSettings(collection)
        PropagateCollectionMaskSettings(
            collection, mask, context.window_manager.bForAllChildren)

        if context.window_manager.bForAllChildren:
            self.report({'INFO'}, "Mask settings applied to all children")
        else:
            self.report({'INFO'}, "Mask settings applied to immediate children")

        return {'FINISHED'}

classes = (
FTB_OT_OverrideRetainTransform_Op, FTB_OT_CollectionNameToMaterial_Op, FTB_OT_ObjectNameToMaterial_Op,
FTB_OT_CopyLocation_Op, FTB_OT_CopyRotation_Op, FTB_OT_CopyScale_Op, FTB_OT_SetLineartSettings_Op,
FTB_OT_SetMatLinks_Op, FTB_OT_ClearMaterialSlots_Op, FTB_OT_PropagateLineArtMaskSettings_Op,
FTB_OT_SetToCenter_Op, FTB_OT_OriginToCursor_Op
)

def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.app.handlers.depsgraph_update_pre.append(UpdateLayerID)
    bpy.types.COLLECTION_PT_lineart_collection.append(drawLineArtMaskButton)


def unregister():
    bpy.types.COLLECTION_PT_lineart_collection.remove(drawLineArtMaskButton)
    bpy.app.handlers.depsgraph_update_pre.remove(UpdateLayerID)

    for c in reversed(classes):
        bpy.utils.unregister_class(c)