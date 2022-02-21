import bpy

from bpy.types import Operator
from bpy.props import BoolProperty


class FTB_OT_Toggle_Face_Orient_Op(Operator):
    bl_idname = "view.toggle_face_orient"
    bl_label = "Toggle Face Orientation"
    bl_description = "Toggle the Face Orientation overlay"

    def execute(self, context):
        if bpy.context.space_data.overlay.show_face_orientation == True:
            bpy.context.space_data.overlay.show_face_orientation = False

        elif bpy.context.space_data.overlay.show_face_orientation == False:
            bpy.context.space_data.overlay.show_face_orientation = True

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


def register():
    bpy.utils.register_class(FTB_OT_Toggle_Face_Orient_Op)
    bpy.utils.register_class(FTB_OT_SelectScaleNonOne_Op)
    bpy.utils.register_class(FTB_OT_SelectScaleNonUniform_Op)
    bpy.utils.register_class(FTB_OT_SelectRotationNonZero_Op)
    bpy.utils.register_class(FTB_OT_SelectLocationNonZero_Op)
    bpy.utils.register_class(FTB_OT_SetToCenter_Op)
    bpy.utils.register_class(FTB_OT_OriginToCursor_Op)
    bpy.utils.register_class(FTB_OT_CheckNgons_Op)
    bpy.utils.register_class(FTB_OT_ValidateMatSlots_Op)
    bpy.utils.register_class(FTB_OT_FindOrphanedObjects_Op)
    bpy.utils.register_class(FTB_OT_FindOrphanTextures_Op)


def unregister():
    bpy.utils.unregister_class(FTB_OT_FindOrphanTextures_Op)
    bpy.utils.unregister_class(FTB_OT_FindOrphanedObjects_Op)
    bpy.utils.unregister_class(FTB_OT_ValidateMatSlots_Op)
    bpy.utils.unregister_class(FTB_OT_CheckNgons_Op)
    bpy.utils.unregister_class(FTB_OT_OriginToCursor_Op)
    bpy.utils.unregister_class(FTB_OT_SetToCenter_Op)
    bpy.utils.unregister_class(FTB_OT_SelectLocationNonZero_Op)
    bpy.utils.unregister_class(FTB_OT_SelectRotationNonZero_Op)
    bpy.utils.unregister_class(FTB_OT_SelectScaleNonUniform_Op)
    bpy.utils.unregister_class(FTB_OT_SelectScaleNonOne_Op)
    bpy.utils.unregister_class(FTB_OT_Toggle_Face_Orient_Op)
