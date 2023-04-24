
import bpy
import string

from bpy.types import Operator
from bpy.app.handlers import persistent

from .. utility_functions.ftb_transform_utils import ob_Copy_Vis_Loc
from .. utility_functions.ftb_transform_utils import ob_Copy_Vis_Rot
from .. utility_functions.ftb_transform_utils import ob_Copy_Vis_Sca
from .. utility_functions.ftb_string_utils import strip_End_Numbers
from .. utility_functions.ftb_path_utils import getAbsoluteFilePath
from .. utility_functions.ftb_string_utils import OS_SEPARATOR
from .. utility_functions import ftb_logging as log


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


def drawLineUsageButton(self, context):
    layout = self.layout
    col = layout.column()
    col.operator("collection.propagate_line_usage")


def PropagateCollectionLineUsage(Collection, Usage):
    if Collection.children:
        for c in Collection.children:
            c.lineart_usage = Usage
            PropagateCollectionLineUsage(c, Usage)


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


class FTB_OT_ResetLineartSettings_Op(Operator):
    bl_idname = "scene.reset_lineart_settings"
    bl_label = "Reset Lineart Usage"
    bl_description = "Reset Lineart Usage for Objects and Collections for entire Scene. Objects will be set to Inherit, collections will be set to Include"
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
        for obj in bpy.data.objects:
            if (obj.library is not None) or (obj.override_library is not None):
                obj.lineart.usage = "INHERIT"

        for coll in bpy.data.collections:
            if (coll.library is not None) or (coll.override_library is not None):
                coll.lineart_usage = "INCLUDE"

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
                if slot.material is None:
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
            self.report(
                {'INFO'},
                "Operation Finished. Successfully cleared " + str(slotCount) + " slots on " + str(objCount) + " objects.")

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


class FTB_OT_PropagateLineUsage_Op(Operator):

    bl_idname = "collection.propagate_line_usage"
    bl_label = "Propagate to child collections"
    bl_description = "Copies the Line Art Usage from this collection to all its children recursively"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        collection = context.collection
        usage = collection.lineart_usage
        PropagateCollectionLineUsage(collection, usage)
        self.report({'INFO'}, "Mask settings applied to all children")
        return {'FINISHED'}


class FTB_OT_LimitToThisViewLayer_Op(Operator):
    bl_idname = "collection.limit_to_view_layer"
    bl_label = "Limit to View Layer"
    bl_description = "Disable active collection in all view layers except the active one"
    bl_options = {'REGISTER', 'UNDO'}

    # should not work when Scene Collection is active

    @classmethod
    def poll(cls, context):
        if bpy.context.collection.name == "Scene Collection":
            return False
        else:
            return True

    def execute(self, context):

        # create list of all view layers except active one
        viewLayerList = list(bpy.context.scene.view_layers)
        viewLayerList.remove(bpy.context.view_layer)

        # count exclude occurrences to notify user in UI
        excludeCount = 0

        for layer in viewLayerList:
            for childcol in layer.layer_collection.children:
                if bpy.context.collection == childcol.collection:
                    childcol.exclude = True
                    excludeCount += 1

        excludeString = "Excluded active collection in " + str(excludeCount) + " other view layers except active layer."

        self.report({'INFO'}, excludeString)
        return {'FINISHED'}


class FTB_OT_GetAbsoluteDataPath_Op(Operator):
    bl_idname = "outliner.get_absolute_path"
    bl_label = "Get Absolute Path"
    bl_description = "Prints absolute Path of selected datablock"
    bl_options = {'REGISTER', 'UNDO'}

    relpath: bpy.props.StringProperty(name="Relative Path", default="")
    absolpath: bpy.props.StringProperty(name="Absolute Path", default="")

    def execute(self, context):

        self.absolpath = (getAbsoluteFilePath(self.relpath))
        bpy.context.window_manager.clipboard = self.absolpath
        return {'FINISHED'}

    def invoke(self, context, event):
        self.absolpath = (getAbsoluteFilePath(self.relpath))
        return bpy.context.window_manager.invoke_popup(self, width=500)


def equalizeSubdiv(obj, useViewportLevel=False, useVisibility=False):
    # ignore linked objects with no override
    if (obj.library is None):
        for mod in obj.modifiers:
            if mod.type == 'SUBSURF':
                if useViewportLevel:
                    if useVisibility:
                        mod.show_render = mod.show_viewport
                    else:
                        mod.render_levels = mod.levels
                else:
                    if useVisibility:
                        mod.show_viewport = mod.show_render

                    else:
                        mod.levels = mod.render_levels


class FTB_OT_EqualizeSubdivision_Op(Operator):
    bl_idname = "object.equalize_subdiv"
    bl_label = "Equalize Subdiv"
    bl_description = "Equalizes between viewport and render subdiv levels"
    bl_options = {'REGISTER', 'UNDO'}

    useVisibility: bpy.props.BoolProperty(
        name='useVisbility',
        default=False
    )

    def execute(self, context):
        wm = bpy.context.window_manager

        # Case limit = All
        if (wm.ftbSubdivEqualScope == 'ALL'):
            for object in bpy.data.objects:
                if (wm.ftbSubdivEqualTarget == 'RENDER'):
                    if self.useVisibility:
                        equalizeSubdiv(obj=object, useVisibility=True)
                    else:
                        equalizeSubdiv(obj=object)

                else:
                    if self.useVisibility:
                        equalizeSubdiv(obj=object, useViewportLevel=True, useVisibility=True)
                    else:
                        equalizeSubdiv(obj=object, useViewportLevel=True)

        # Case limit = View Layer
        if (wm.ftbSubdivEqualScope == 'VIEW_LAYER'):
            for object in bpy.context.view_layer.objects:
                if (wm.ftbSubdivEqualTarget == 'RENDER'):
                    if self.useVisibility:
                        equalizeSubdiv(obj=object, useVisibility=True)
                    else:
                        equalizeSubdiv(obj=object)
                else:
                    if self.useVisibility:
                        equalizeSubdiv(obj=object, useViewportLevel=True, useVisibility=True)
                    else:
                        equalizeSubdiv(obj=object, useViewportLevel=True)

        if (wm.ftbSubdivEqualScope == 'SELECTION'):
            for object in bpy.context.selected_objects:
                if (wm.ftbSubdivEqualTarget == 'RENDER'):
                    if self.useVisibility:
                        equalizeSubdiv(obj=object, useViewportLevel=False, useVisibility=True)
                    else:
                        equalizeSubdiv(obj=object, useViewportLevel=False)
                else:
                    if self.useVisibility:
                        equalizeSubdiv(obj=object, useViewportLevel=True, useVisibility=True)
                    else:
                        equalizeSubdiv(obj=object, useViewportLevel=True)

        return {'FINISHED'}


def get_objects():
    """ Returns all the objects in the scene, or a given collection, or in a selection, depending on wm.ftbBoolScope """
    wm = bpy.context.window_manager

    if wm.ftbBoolScope == 'ALL':
        return bpy.context.scene.objects

    if wm.ftbBoolScope == 'COLLECTION':
        return wm.ftbBoolCollection.all_objects

    if wm.ftbBoolScope == 'SELECTION':
        return bpy.context.selected_objects


def refresh_ui():
    """Redraw the ui once an async thread has completed"""
    for windowManager in bpy.data.window_managers:
        for window in windowManager.windows:
            for area in window.screen.areas:
                area.tag_redraw()


class FTB_OT_SetExactBooleans_OP(Operator):
    bl_idname = "object.set_exact_booleans"
    bl_label = "Exact"
    bl_description = "Sets all Booleans on all objects in the File or given Collection to Exact with Self Intersection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in get_objects():
            for mod in obj.modifiers:
                if mod.type == 'BOOLEAN':
                    if obj.override_library:
                        # Add the Boolean modifier property to the overriden properties in the override_library of the object
                        # This fixes the inconsistent overrides that happen, when the property gets set.
                        override = obj.override_library.properties.add('modifiers["' + mod.name + '"].solver')
                        override.operations.add('REPLACE')

                        override = obj.override_library.properties.add('modifiers["' + mod.name + '"].use_self')
                        override.operations.add('REPLACE')
                    mod.solver = 'EXACT'
                    mod.use_self = True

        # New overrides are only visible after refreshing the UI
        refresh_ui()
        return {'FINISHED'}


class FTB_OT_SetFastBooleans_OP(Operator):
    bl_idname = "object.set_fast_booleans"
    bl_label = "Fast"
    bl_description = "Sets all Booleans on all objects in the File or given Collection to Fast"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        for obj in get_objects():
            for mod in obj.modifiers:
                if mod.type == 'BOOLEAN':
                    if obj.override_library:
                        # Add the Boolean modifier property to the overriden properties in the override_library of the object
                        # This fixes the inconsistent overrides that happen, when the property gets set.
                        override = obj.override_library.properties.add('modifiers["' + mod.name + '"].solver')
                        override.operations.add('REPLACE')
                    mod.solver = 'FAST'

        # New overrides are only visible after refreshing the UI
        refresh_ui()
        return {'FINISHED'}


class FTB_OT_HideBooleansViewport_OP(Operator):
    bl_idname = "object.hide_booleans_viewport"
    bl_label = "Hide Viewport"
    bl_description = "Sets all Booleans on all objects in the File or given Collection to Hidden in the Viewport"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in get_objects():
            for mod in obj.modifiers:
                if mod.type == 'BOOLEAN':
                    if obj.override_library:
                        # Add the Boolean modifier property to the overriden properties in the override_library of the object
                        # This fixes the inconsistent overrides that happen, when the property gets set.
                        override = obj.override_library.properties.add('modifiers["' + mod.name + '"].show_viewport')
                        override.operations.add('REPLACE')
                    mod.show_viewport = False

        # New overrides are only visible after refreshing the UI
        refresh_ui()
        return {'FINISHED'}


class FTB_OT_UnhideBooleansViewport_OP(Operator):
    bl_idname = "object.unhide_booleans_viewport"
    bl_label = "Visible Viewport"
    bl_description = "Sets all Booleans on all objects in the File or given Collection to visible in the Viewport"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in get_objects():
            for mod in obj.modifiers:
                if mod.type == 'BOOLEAN':
                    if obj.override_library:
                        # Add the Boolean modifier property to the overriden properties in the override_library of the object
                        # This fixes the inconsistent overrides that happen, when the property gets set.
                        override = obj.override_library.properties.add('modifiers["' + mod.name + '"].show_viewport')
                        override.operations.add('REPLACE')
                    mod.show_viewport = True

        # New overrides are only visible after refreshing the UI
        refresh_ui()
        return {'FINISHED'}


class FTB_OT_HideBooleansRender_OP(Operator):
    bl_idname = "object.hide_booleans_render"
    bl_label = "Hide Render"
    bl_description = "Sets all Booleans on all objects in the File or given Collection to Hidden in the Render"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in get_objects():
            for mod in obj.modifiers:
                if mod.type == 'BOOLEAN':
                    if obj.override_library:
                        # Add the Boolean modifier property to the overriden properties in the override_library of the object
                        # This fixes the inconsistent overrides that happen, when the property gets set.
                        override = obj.override_library.properties.add('modifiers["' + mod.name + '"].show_render')
                        override.operations.add('REPLACE')

                    mod.show_render = False

        # New overrides are only visible after refreshing the UI
        refresh_ui()
        return {'FINISHED'}


class FTB_OT_UnhideBooleansRender_OP(Operator):
    bl_idname = "object.unhide_booleans_render"
    bl_label = "Visible Render"
    bl_description = "Sets all Booleans on all objects in the File or given Collection to Visible in the Render"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in get_objects():
            for mod in obj.modifiers:
                if mod.type == 'BOOLEAN':
                    if obj.override_library:
                        # Add the Boolean modifier property to the overriden properties in the override_library of the object
                        # This fixes the inconsistent overrides that happen, when the property gets set.
                        override = obj.override_library.properties.add('modifiers["' + mod.name + '"].show_render')
                        override.operations.add('REPLACE')

                    mod.show_render = True

        # New overrides are only visible after refreshing the UI
        refresh_ui()
        return {'FINISHED'}


class FTB_OT_SelfIntersectionBoolean_OP(Operator):
    bl_idname = "object.self_intersection_booleans"
    bl_label = "Self Intersection"
    bl_description = "Enables self intersection on all boolean modifers for the entire scene"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def description(cls, context, properties):
        wm = context.window_manager
        if wm.ftbBoolScope == 'COLLECTION':
            _desc = "the active collection"
        elif wm.ftbBoolScope == 'SELECTION':
            _desc = "your current selection"
        else:
            _desc = "the entire scene"
        return f"Enables self intersection on all boolean modifers for {_desc}"

    def execute(self, context):
        _mod_count = 0
        _anim_count = 0
        _data_path = 'modifiers["Boolean"].use_self'
        for obj in get_objects():
            if obj.type != 'MESH':
                continue

            for mod in obj.modifiers:
                if mod.type != 'BOOLEAN':
                    continue

                if mod.use_self:
                    continue

                if obj.override_library:
                    # Add the Boolean modifier property to the overriden properties in the override_library of the object
                    # This fixes the inconsistent overrides that happen, when the property gets set.
                    override = obj.override_library.properties.add(_data_path)
                    override.operations.add('REPLACE')

                mod.use_self = True
                log.console(self, log.Severity.INFO,
                            f"Object: {obj.name_full} Boolean modifier - Self Intersection enabled!")
                _mod_count += 1

            if not obj.visible_get() or not obj.animation_data or not obj.animation_data.action:
                continue

            for fcurve in obj.animation_data.action.fcurves:
                if fcurve.data_path == _data_path:
                    log.console(self, log.Severity.WARNING,
                                f"Object: {obj.name_full} - Self Intersection property is animated!")
                    _anim_count += 1
                    continue

        # New overrides are only visible after refreshing the UI
        refresh_ui()
        if _mod_count < 1:
            _report = f"No changes. Either all modifiers are all set or no modifiers found"
        else:
            _report = f"Self Intersection enabled for {_mod_count} {('modifier','modifiers' )[_mod_count > 1]}"

        if _anim_count > 0:
            _report += f". {_anim_count} {('modifier','modifiers' )[_anim_count > 1]} keyframed!"

        _logtype = (log.Severity.INFO, log.Severity.WARNING)[_anim_count > 0]
        log.report(self, _logtype, _report)
        return {'FINISHED'}


class FTB_OT_UseHoleTolerantBoolean_OP(Operator):
    bl_idname = "object.hole_tolerant_booleans"
    bl_label = "Hole Tolerant"
    bl_description = "Enables Hole Tolerant on all boolean modifers for the entire scene"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def description(cls, context, properties):
        wm = context.window_manager
        if wm.ftbBoolScope == 'COLLECTION':
            _desc = "the active collection"
        elif wm.ftbBoolScope == 'SELECTION':
            _desc = "your current selection"
        else:
            _desc = "the entire scene"
        return f"Enables Hole Tolerant on all boolean modifers for {_desc}"

    def execute(self, context):
        _mod_count = 0
        _anim_count = 0
        _data_path = 'modifiers["Boolean"].use_hole_tolerant'
        for obj in get_objects():
            if obj.type != 'MESH':
                continue

            for mod in obj.modifiers:
                if mod.type != 'BOOLEAN':
                    continue

                if mod.use_hole_tolerant:
                    continue

                if obj.override_library:
                    # Add the Boolean modifier property to the overriden properties in the override_library of the object
                    # This fixes the inconsistent overrides that happen, when the property gets set.
                    override = obj.override_library.properties.add(_data_path)
                    override.operations.add('REPLACE')

                mod.use_hole_tolerant = True
                log.console(self, log.Severity.INFO,
                            f"Object: {obj.name_full} Boolean modifier - Hole Tolerant enabled!")
                _mod_count += 1

            if not obj.visible_get() or not obj.animation_data or not obj.animation_data.action:
                continue

            for fcurve in obj.animation_data.action.fcurves:
                if fcurve.data_path == _data_path:
                    log.console(self, log.Severity.WARNING,
                                f"Object: {obj.name_full} - Hole Tolerant property is animated!")
                    _anim_count += 1
                    continue

        # New overrides are only visible after refreshing the UI
        refresh_ui()
        if _mod_count < 1:
            _report = f"No changes. Either all modifiers are all set or no modifiers found"
        else:
            _report = f"Hole Tolerant enabled for {_mod_count} {('modifier','modifiers' )[_mod_count > 1]}"

        if _anim_count > 0:
            _report += f". {_anim_count} {('modifier','modifiers' )[_anim_count > 1]} keyframed!"

        _logtype = (log.Severity.INFO, log.Severity.WARNING)[_anim_count > 0]
        log.report(self, _logtype, _report)
        return {'FINISHED'}


class FTB_OT_HideLatticeModifiers_Op(Operator):
    bl_idname = "object.hide_lattice_modifiers"
    bl_label = "Set Lattice Modifiers"
    bl_description = "Hides/Shows Lattice Modifiers in Viewport"
    bl_options = {'REGISTER', 'UNDO'}

    showViewport: bpy.props.BoolProperty(
        name="disable",
        default=False
    )

    def execute(self, context):

        objList = list()
        wm = bpy.context.window_manager

        if wm.ftbLatticeScope == 'ALL':
            objList = bpy.context.scene.objects

        if wm.ftbLatticeScope == 'SELECTION':
            if not bpy.context.selected_objects:
                self.report({'ERROR'}, "No objects selected")
                return {'CANCELLED'}
            else:
                objList = bpy.context.selected_objects

        for obj in objList:
            for mod in obj.modifiers:
                if mod.type == 'LATTICE':
                    if obj.override_library:
                        # Add the lattice modifier property to the overriden properties in the override_library of the object
                        # This fixes the inconsistent overrides that happen, when the property gets set.
                        override = obj.override_library.properties.add('modifiers["' + mod.name + '"].show_viewport')
                        override.operations.add('REPLACE')
                    if self.showViewport:
                        mod.show_viewport = True
                    else:
                        mod.show_viewport = False

        # New overrides are only visible after refreshing the UI
        refresh_ui()
        return {'FINISHED'}

class FTB_OT_ConformVisibilites_OP(Operator):
    bl_idname = "ftb.conform_visibilities"
    bl_label = "Conform Visibilities"
    bl_description = "Conforms visibilites to Render or Viewport visibilites."
    bl_options = {'REGISTER', 'UNDO'}

    use_render: bpy.props.BoolProperty(
        name="use_render",
        default=True
    )

    @classmethod
    def poll(cls, context):
        wm = context.window_manager
        if wm.ftbVisibilityScope in {'OBJ_IN_COLLECTION', 'COL_IN_COLLECTION'}:
            if not wm.ftbVisibilityCollection:
                return False
        return True

    def execute(self, context):

        wm = context.window_manager

        if wm.ftbVisibilityScope == 'OBJECTS' or wm.ftbVisibilityScope == 'OBJ_IN_COLLECTION':
            
            objects_to_conform = []
            if wm.ftbVisibilityScope == 'OBJECTS':
                objects_to_conform = context.scene.objects
            if wm.ftbVisibilityScope == 'COLLECTION':
                objects_to_conform = wm.ftbVisibilityCollection.all_objects

            for obj in objects_to_conform:
                if self.use_render:
                    if obj.hide_render:
                        obj.hide_set(True)
                        obj.hide_viewport = True
                    else:
                        obj.hide_set(False)
                        obj.hide_viewport = False
                else:
                    if obj.hide_viewport or obj.hide_get():
                        obj.hide_render = True
                    else:
                        obj.hide_render = False

        if wm.ftbVisibilityScope in {'COLLECTIONS', 'COL_IN_COLLECTION'}:
            collections_to_conform = []
            if wm.ftbVisibilityScope == 'COLLECTIONS':
                collections_to_conform = context.scene.collection.children_recursive
            
            if wm.ftbVisibilityScope == 'COL_IN_COLLECTION':
                collections_to_conform = wm.ftbVisibilityCollection.children_recursive
                collections_to_conform.append(wm.ftbVisibilityCollection)

            for collection in collections_to_conform:
                layer_children_recursive = [col for col in self.traverse_tree(context.view_layer.layer_collection)]
                view_layer_collection = next((col for col in layer_children_recursive if col.name == collection.name), None)

                if self.use_render:
                    if collection.hide_render:
                        collection.hide_viewport = True
                        view_layer_collection.hide_viewport = True
                    else:
                        collection.hide_viewport = False
                        view_layer_collection.hide_viewport = False
                else:
                    if collection.hide_viewport or view_layer_collection.hide_viewport:
                        collection.hide_render = True
                    else:
                        collection.hide_render = False
        return {'FINISHED'}
    
    def traverse_tree(self, t):
        yield t
        for child in t.children:
            yield from self.traverse_tree(child)

class FTB_OT_SplitInShots_OP(Operator):
    bl_idname = "scene.split_in_shots"
    bl_label = "Split File in Shots"
    bl_description = ("Splits sequence file in shots by saving copies with an unique file name, setting start/end frame"
                      " ranges and the active camera automatically")
    bl_options = {'REGISTER'}

    naming_mask_is_valid: bool = True

    def is_valid_name(self, name: str) -> bool:
        _valid_chars = string.ascii_letters + string.digits + "-_#"
        for c in name:
            if c not in _valid_chars:
                return False
        return name != ""

    end_frame: bpy.props.IntProperty(
        name="Sequence end frame",
        description="Last frame of this sequence",
        default=0
    )

    naming_mask: bpy.props.StringProperty(
        name="Filename",
        description="Naming mask used for saving splits. Use ### as shot number placeholder for shot filenames",
        default=""
    )

    dopesheet_editor: bpy.types.Area = None

    @classmethod
    def poll(cls, context):
        for area in context.screen.areas:
            if area.type == 'DOPESHEET_EDITOR':
                cls.dopesheet_editor = area
                break
            cls.dopesheet_editor = None

        if not cls.dopesheet_editor:
            cls.poll_message_set("Need Timeline window in current workspace")
            return False

        return True

    def invoke(self, context, event):
        self.end_frame = context.scene.frame_end
        self.naming_mask = f"{bpy.data.filepath.split(OS_SEPARATOR)[-1][:-6]}_###"
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "end_frame")
        if not self.naming_mask_is_valid:
            layout.alert = True
            layout.label(text="Only letters, digits, -_# are allowed in names!")
            layout.label(text="No whitespaces and Name may not be empty!")
            layout.label(text="Use ### character set to designate shot number in file name!")
        layout.prop(self, "naming_mask")
        layout.alert = False

    def execute(self, context):

        if "###" not in self.naming_mask or not self.is_valid_name(self.naming_mask):
            self.naming_mask_is_valid = False
            return context.window_manager.invoke_props_dialog(self, width=400)

        initial_frame_start = context.scene.frame_start
        initial_end_frame = context.scene.frame_end
        initial_current_frame = context.scene.frame_current
        file_dir = bpy.data.filepath[:bpy.data.filepath.rfind(OS_SEPARATOR)+1]

        # check for existing end marker at last sequence frame
        end_marker = None
        for marker in context.scene.timeline_markers:
            if marker.frame == self.end_frame:
                end_marker = marker

        # create an end marker if there is none
        if not end_marker:
            context.scene.frame_current = self.end_frame
            with bpy.context.temp_override(area=self.dopesheet_editor):
                try:
                    bpy.ops.marker.add()
                except:
                    log.report(self, log.Severity.ERROR, "Failed to add end marker")
                    return {'CANCELLED'}

            context.scene.timeline_markers[-1].name = "end_of_scene"

        context.scene.frame_current = initial_current_frame

        # find markers for corresponding shots, set start + end frames and save a copy
        for i, marker in enumerate(sorted(context.scene.timeline_markers, key=lambda m: m.frame)):

            if i == len(context.scene.timeline_markers)-1:
                continue

            if not marker.camera:
                continue

            shot_number = marker.camera.name.split(".")[-1]
            next_marker = None
            for nm in sorted(context.scene.timeline_markers, key=lambda m: m.frame):
                if nm.camera and nm.frame > marker.frame:
                    next_marker = nm
                    break

            range_end = initial_end_frame
            if next_marker:
                range_end = next_marker.frame-1

            context.scene.frame_start = marker.frame
            context.scene.frame_end = range_end
            context.scene.camera = marker.camera

            new_filename = f"{self.naming_mask.replace('###', shot_number)}.blend"
            new_filepath = file_dir + new_filename

            #print(f"Saving {new_filepath} with range: {marker.frame} - {range_end}")
            try:
                bpy.ops.wm.save_as_mainfile(filepath=new_filepath, copy=True)
            except:
                log.report(self, log.Severity.ERROR, f"Failed saving file - {new_filename}")
                return {'CANCELLED'}

        context.scene.frame_start = initial_frame_start
        context.scene.frame_end = initial_end_frame
        log.report(self, log.Severity.INFO, f"Shot splitting successful")
        return {'FINISHED'}


class FTB_OT_SetShotRange_OP(Operator):
    bl_idname = "scene.set_shot_range"
    bl_label = "FTB: Set Shot Range"
    bl_description = ("Sets start and end frame based on selected current frame and camera markers next to it")
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.area.type != 'DOPESHEET_EDITOR':
            cls.poll_message_set("Need Timeline window in current workspace")
            return False
        return True

    def execute(self, context):
        current_frame = context.scene.frame_current
        range_start = 0
        range_end = 0
        for i, marker in enumerate(sorted(context.scene.timeline_markers, key=lambda m: m.frame)):
            if marker.frame <= current_frame and marker.camera:
                range_start = marker.frame
            if marker.frame > current_frame and (marker.camera or i == len(context.scene.timeline_markers)-1):
                range_end = (marker.frame - 1, marker.frame)[i == len(context.scene.timeline_markers)-1]
                break

        if range_end == 0 or range_start == 0:
            log.report(self, log.Severity.ERROR, "Could not locate valid start or end marker")
            return {'CANCELLED'}
        context.scene.frame_start = range_start
        context.scene.frame_end = range_end
        log.report(self, log.Severity.INFO, f"Range set from {range_start} to {range_end}")
        return {'FINISHED'}


classes = (
    FTB_OT_OverrideRetainTransform_Op, FTB_OT_CollectionNameToMaterial_Op, FTB_OT_ObjectNameToMaterial_Op,
    FTB_OT_CopyLocation_Op, FTB_OT_CopyRotation_Op, FTB_OT_CopyScale_Op, FTB_OT_SetLineartSettings_Op,
    FTB_OT_SetMatLinks_Op, FTB_OT_ClearMaterialSlots_Op, FTB_OT_PropagateLineUsage_Op,
    FTB_OT_SetToCenter_Op, FTB_OT_OriginToCursor_Op, FTB_OT_LimitToThisViewLayer_Op,
    FTB_OT_GetAbsoluteDataPath_Op, FTB_OT_ResetLineartSettings_Op, FTB_OT_EqualizeSubdivision_Op,
    FTB_OT_SetExactBooleans_OP, FTB_OT_SetFastBooleans_OP, FTB_OT_HideBooleansViewport_OP,
    FTB_OT_UnhideBooleansViewport_OP, FTB_OT_HideBooleansRender_OP, FTB_OT_UnhideBooleansRender_OP,
    FTB_OT_SelfIntersectionBoolean_OP, FTB_OT_UseHoleTolerantBoolean_OP,
    FTB_OT_HideLatticeModifiers_Op, FTB_OT_ConformVisibilites_OP, FTB_OT_SplitInShots_OP, FTB_OT_SetShotRange_OP
)


def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.app.handlers.depsgraph_update_pre.append(UpdateLayerID)
    bpy.types.COLLECTION_PT_lineart_collection.append(drawLineUsageButton)


def unregister():
    bpy.types.COLLECTION_PT_lineart_collection.remove(drawLineUsageButton)
    bpy.app.handlers.depsgraph_update_pre.remove(UpdateLayerID)

    for c in reversed(classes):
        bpy.utils.unregister_class(c)
