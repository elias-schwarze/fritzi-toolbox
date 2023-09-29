
import bpy
import inspect
import string
import sys

from bpy.types import Operator

from .. utility_functions.ftb_transform_utils import ob_Copy_Vis_Loc
from .. utility_functions.ftb_transform_utils import ob_Copy_Vis_Rot
from .. utility_functions.ftb_transform_utils import ob_Copy_Vis_Sca
from .. utility_functions.ftb_string_utils import strip_End_Numbers
from .. utility_functions.ftb_path_utils import getAbsoluteFilePath
from .. utility_functions.ftb_string_utils import OS_SEPARATOR
from .. utility_functions import ftb_logging as log


END_MARKER_NAME = "end_of_sequence"


def DecToBin(n, OutBinaryArray):
    if not n == 0:
        OutBinaryArray.append(n % 2)
        DecToBin(n >> 1, OutBinaryArray)


def BinToDec(BinaryArray):
    n = 0
    for i in reversed(range(len(BinaryArray))):
        n += BinaryArray[i] * pow(2, i)
    return n


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

            context.scene.timeline_markers[-1].name = END_MARKER_NAME

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

            # print(f"Saving {new_filepath} with range: {marker.frame} - {range_end}")
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

    end_frame_number: bpy.props.IntProperty(name="New End Frame Number",
                                            default=0)
    range_start = 0
    range_end = 0
    no_end_marker_found = False

    @classmethod
    def poll(cls, context):
        if context.area.type != 'DOPESHEET_EDITOR':
            cls.poll_message_set("Need Timeline window in current workspace")
            return False
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Could not find valid end marker.")
        layout.label(text="Please enter a frame number to add a new marker:")
        if self.range_end <= self.range_start:
            layout.alert = True
            layout.label(text=f"Frame end number must be greater than {self.range_start}")
            layout.alert = False
        self.layout.prop(self, "end_frame_number")
        self.range_end = self.end_frame_number

    def execute(self, context):
        current_frame = context.scene.frame_current
        if self.no_end_marker_found:
            if self.range_end <= self.range_start:
                return context.window_manager.invoke_props_dialog(self, width=300)

            try:
                context.scene.frame_current = self.range_end
                bpy.ops.marker.add()
            except:
                log.report(self, log.Severity.ERROR, "Failed to add marker")
                return {'CANCELLED'}

            context.scene.timeline_markers[-1].name = END_MARKER_NAME
            context.scene.frame_current = current_frame

        for i, marker in enumerate(sorted(context.scene.timeline_markers, key=lambda m: m.frame)):
            if marker.frame <= current_frame and marker.camera:
                self.range_start = marker.frame
            if marker.frame > current_frame and (marker.camera or i == len(context.scene.timeline_markers)-1):
                self.range_end = (marker.frame - 1, marker.frame)[i == len(context.scene.timeline_markers)-1]
                self.no_end_marker_found = False
                break

        if self.range_start == 0:
            log.report(self, log.Severity.ERROR, "Could not locate valid start marker")
            return {'CANCELLED'}

        if self.range_end == 0:
            self.end_frame_number = context.scene.frame_end
            self.no_end_marker_found = True
            return context.window_manager.invoke_props_dialog(self, width=300)

        context.scene.frame_start = self.range_start
        context.scene.frame_end = self.range_end
        log.report(self, log.Severity.INFO, f"Range set from {self.range_start} to {self.range_end}")
        return {'FINISHED'}


class FTB_OT_SetCameraClipping(Operator):
    bl_idname = "scene.set_camera_clipping"
    bl_label = "Set Camera Clipping"
    bl_description = "Sets \"Clip Start\" and \"Clip End\" attribute for all cameras in the scene."
    bl_options = {'REGISTER', 'UNDO'}

    new_clip_start: bpy.props.FloatProperty(name="New Clip Start",
                                            default=1.0,
                                            min=0.001,
                                            precision=1)

    new_clip_end: bpy.props.FloatProperty(name="New Clip Start",
                                          default=1000.0,
                                          precision=1)

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.prop(self, "new_clip_start")
        self.layout.prop(self, "new_clip_end")

    def execute(self, context):
        for camera in bpy.data.cameras:
            camera.clip_start = self.new_clip_start
            camera.clip_end = self.new_clip_end

        return {'FINISHED'}


class FTB_OT_RemoveEmptyCollection(Operator):
    bl_idname = "outliner.remove_empty_collection"
    bl_label = "Remove Empty Collections"
    bl_description = "Removes all collections inside the active collection which contain no objects"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.area.type != 'OUTLINER':
            return False
        return True

    def execute(self, context):
        collection: bpy.types.Collection
        for collection in context.collection.children_recursive:
            if len(collection.all_objects) > 0:
                continue
            bpy.data.collections.remove(collection)

        if len(context.collection.all_objects) < 1:
            bpy.data.collections.remove(context.collection)

        return {'FINISHED'}


def add_driver(source, target, prop, dataPath, index=-1, negative=False, func=""):
    # from https://blender.stackexchange.com/questions/39127/how-to-put-together-a-driver-with-python
    # slightly modified for my needs
    ''' Add driver to source prop (at index), driven by target dataPath '''

    if index != -1:
        d = source.driver_add(prop, index).driver
    else:
        d = source.driver_add(prop).driver

    v = d.variables.new()
    v.name = prop
    v.targets[0].id = target
    v.targets[0].data_path = dataPath

    d.expression = f"{func}" if func else v.name
    d.expression = d.expression if not negative else "-1 * " + d.expression


class FTB_OT_AddFritziLightRig(Operator):
    bl_idname = "object.add_fritzi_lightrig"
    bl_label = "Fritzi Sun Light"
    bl_description = "Adds a custom light rig using two suns controlled by an empty with custom properties"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and context.space_data.type == 'VIEW_3D'

    def spawn_fritzi_sun(self, name) -> bpy.types.Object:
        bpy.ops.object.light_add(type='SUN', radius=1, align='WORLD')
        obj = bpy.context.active_object
        obj.name = name
        obj.select_set(False)
        obj.hide_select = True

        return obj

    def add_custom_property(self, object, prop_name, default, min_max, precision=3, description="", subtype=""):
        if prop_name in object:
            return

        object[prop_name] = default

        ui = object.id_properties_ui(prop_name)

        ui.update(description=description)
        ui.update(default=default)
        ui.update(min=min_max[0], soft_min=min_max[0])
        ui.update(max=min_max[1], soft_max=min_max[1])
        ui.update(precision=precision)

        if subtype != "":
            ui.update(subtype=subtype)

        # update dependencies to register new property
        object.update_tag()

    def execute(self, context):

        bpy.ops.object.empty_add(type='SINGLE_ARROW', align='WORLD', rotation=(3.1459, 0, 0))
        rig_root = context.active_object
        rig_root.name = "fritzi_sun_rig"

        sun_light = self.spawn_fritzi_sun("Light")
        sun_bleed = self.spawn_fritzi_sun("Bleed")

        sun_light.parent = rig_root
        sun_light.matrix_parent_inverse = rig_root.matrix_world.inverted()
        sun_bleed.parent = rig_root
        sun_bleed.matrix_parent_inverse = rig_root.matrix_world.inverted()

        rig_root.select_set(True)
        context.view_layer.objects.active = rig_root

        # check for LIGHTS Collection and link everthing to it if it exists
        active_collection = context.collection
        lights_collection = None
        lf_index = bpy.data.collections.find("LIGHTS")
        if lf_index != -1:
            lights_collection = bpy.data.collections[lf_index]

        if lights_collection:
            lights_collection.objects.link(rig_root)
            lights_collection.objects.link(sun_light)
            lights_collection.objects.link(sun_bleed)
            active_collection.objects.unlink(rig_root)
            active_collection.objects.unlink(sun_light)
            active_collection.objects.unlink(sun_bleed)

        intensity_range = (0.0, 1000.0)
        color_range = (0.0, 1.0)
        bias_range = (0.0, 360.0)
        self.add_custom_property(rig_root, "Bleed Amount", 1.0, bias_range)
        self.add_custom_property(rig_root, "Bleed Color", (1.0, 1.0, 0.597), color_range, precision=4, subtype='COLOR')
        self.add_custom_property(rig_root, "Bleed Intensity", 12.0, intensity_range)
        self.add_custom_property(rig_root, "Light Color", (1.0, 1.0, 0.847), color_range, precision=4, subtype='COLOR')
        self.add_custom_property(rig_root, "Light Intensity", 25.0, intensity_range)
        self.add_custom_property(rig_root, "Light Shadow Bias", 0.0, bias_range)

        add_driver(sun_light.data, rig_root, "energy", "[\"Light Intensity\"]")
        add_driver(sun_light.data, rig_root, "angle", "[\"Light Shadow Bias\"]", func="radians(angle)")
        add_driver(sun_light.data, rig_root, "color", "[\"Light Color\"][0]", index=0)
        add_driver(sun_light.data, rig_root, "color", "[\"Light Color\"][1]", index=1)
        add_driver(sun_light.data, rig_root, "color", "[\"Light Color\"][2]", index=2)

        add_driver(sun_bleed.data, rig_root, "energy", "[\"Bleed Intensity\"]")
        add_driver(sun_bleed.data, rig_root, "color", "[\"Bleed Color\"][0]", index=0)
        add_driver(sun_bleed.data, rig_root, "color", "[\"Bleed Color\"][1]", index=1)
        add_driver(sun_bleed.data, rig_root, "color", "[\"Bleed Color\"][2]", index=2)

        # add driver for bleed amount
        d = sun_bleed.data.driver_add("angle").driver

        v = d.variables.new()
        v.name = "bias"
        v.targets[0].id = rig_root
        v.targets[0].data_path = "[\"Light Shadow Bias\"]"

        v = d.variables.new()
        v.name = "bleed"
        v.targets[0].id = rig_root
        v.targets[0].data_path = "[\"Bleed Amount\"]"

        d.expression = "radians(bias+bleed)"

        return {'FINISHED'}


class FTB_OT_SetFritziPropShaderAttributes(Operator):
    bl_idname = "scene.set_fritzi_shader_attributes"
    bl_label = "Set Fritzi Shader Attributes"
    bl_description = "Sets Fritzi Shader Attributes by name to a new value. Attribute must be a single numerical value"
    bl_options = {'REGISTER', 'UNDO'}

    new_value: bpy.props.FloatProperty(name="New Value",
                                            default=1000.0,
                                            min=0.000,
                                            precision=1)

    input_name: bpy.props.StringProperty(name="Name of desired Input to change",
                                         default="Shaded Range Steps")

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.prop(self, "input_name")
        self.layout.prop(self, "new_value")

    def execute(self, context):

        def set_shaded_steps_recursivly(node: bpy.types.NodeGroup, input_name: str):
            if node.type != 'GROUP':
                return
            if not node.node_tree:
                return
            if node.node_tree.name.startswith("shader-Fritzi_Props"):
                if input_name not in node.inputs:
                    return
                if node.inputs[input_name].type != 'VALUE':
                    return
                node.inputs[input_name].default_value = self.new_value
            else:
                if input_name in node.inputs:
                    if node.inputs[input_name].type != 'VALUE':
                        return
                    node.inputs[input_name].default_value = self.new_value

                for grp_node in node.node_tree.nodes:
                    set_shaded_steps_recursivly(grp_node, input_name)

        for material in bpy.data.materials:
            if not material.node_tree:
                continue

            for node in material.node_tree.nodes:
                if node.type != 'GROUP':
                    continue

                set_shaded_steps_recursivly(node, self.input_name)

        return {'FINISHED'}


class FTB_OT_PurgeCollection(Operator):
    bl_idname = "collection.purge"
    bl_label = "FTB: Purge Collection"
    bl_description = "Hard deletes all objects inside active collection even if they are linked or referenced elsewhere"
    bl_options = {'REGISTER', 'UNDO'}

    active_collection: bpy.types.Collection = None

    @classmethod
    def poll(cls, context):
        if context.mode != 'OBJECT':
            cls.poll_message_set("Must be in OBJECT mode!")
            return False

        cls.active_collection = context.collection
        return True

    def execute(self, context):
        if not self.active_collection:
            message = "No active collection selected!"
            log.report(self, log.Severity.ERROR, message)
            return {'CANCELLED'}

        for i in range(len(self.active_collection.all_objects)):
            try:
                bpy.data.objects.remove(self.active_collection.all_objects[0])
            except:
                message = f"Could not delete object \"{self.active_collection.all_objects[0].name}\""
                log.console(self, log.Severity.WARNING, message)

        collection_is_empty = len(self.active_collection.all_objects) < 1
        if collection_is_empty:
            try:
                message = f"Collection \"{self.active_collection.name}\" purged"
                bpy.data.collections.remove(self.active_collection)
            except:
                message = f"Could not delete collection \"{self.active_collection.name}\""
                log.console(self, log.Severity.WARNING, message)
        else:
            message = f"Could not delete all objects. Consider manual clean up"

        log.report(self, (log.Severity.WARNING, log.Severity.INFO)[collection_is_empty], message)
        return {'FINISHED'}


classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)


def register():
    for c in classes:
        if "FTB_" not in c[0]:
            continue
        bpy.utils.register_class(globals()[c[0]])

    bpy.types.COLLECTION_PT_lineart_collection.append(drawLineUsageButton)


def unregister():
    bpy.types.COLLECTION_PT_lineart_collection.remove(drawLineUsageButton)

    for c in reversed(classes):
        if "FTB_" not in c[0]:
            continue
        bpy.utils.unregister_class(globals()[c[0]])
