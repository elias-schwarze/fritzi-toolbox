import bpy

from bpy.types import Operator

from ..utility_functions.ftb_transform_utils import ob_Copy_Vis_Loc
from ..utility_functions.ftb_transform_utils import ob_Copy_Vis_Rot
from ..utility_functions.ftb_transform_utils import ob_Copy_Vis_Sca


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
        for o in bpy.data.objects:
            if o.type == 'MESH':
                if o.scale[0] != 1 or o.scale[1] != 1 or o.scale[2] != 1:
                    o.select_set(True)

        counter = 0
        for obj in bpy.context.selected_objects:
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
        for o in bpy.data.objects:
            if o.type == 'MESH':
                if not (o.scale[0] == o.scale[1] == o.scale[2]):
                    o.select_set(True)

        counter = 0
        for obj in bpy.context.selected_objects:
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

    # should work in edit and object mode
    @classmethod
    def poll(cls, context):
        obj = context.object

        if obj:
            if obj.mode == "OBJECT" and obj.type == 'MESH':
                return True

            elif obj.mode == "EDIT" and obj.type == 'MESH':
                return True

        return False

    def invoke(self, context, event):
        obj = context.object

        if obj and obj.mode == 'OBJECT':
            bpy.ops.object.mode_set(mode='EDIT')
            return self.execute(context)

        elif obj != None and obj.mode == 'EDIT':
            return self.execute(context)

        else:
            self.report({'ERROR'}, "Invalid Selection")
            return {'CANCELLED'}

    def execute(self, context):
        obj = context.object
        bpy.ops.mesh.select_face_by_sides(
            number=4, type='GREATER', extend=False)

        currentMesh = bpy.context.object.data
        ngonCount = currentMesh.count_selected_items()[2]
        self.report({'INFO'}, str(ngonCount) + " Ngons in Object")
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

            if not (bpy.context.collection):
                self.report({'ERROR'}, "No active collection")
                return {'CANCELLED'}

            for obj in bpy.context.collection.all_objects:
                if (obj.type in ['MESH', 'CURVE', 'SURFACE']):

                    for slot in obj.material_slots:
                        if slot.link == 'DATA':
                            objList.append(obj)

        else:
            for obj in bpy.context.view_layer.objects:
                if (obj.type == ['MESH', 'CURVE', 'SURFACE']):

                    for slot in obj.material_slots:
                        if slot.link == 'DATA':
                            objList.append(obj)

        if (objList):
            self.report({'WARNING'}, "Found " + str(len(objList)) +
                        " Objects with incorrect material slots")
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


def register():
    bpy.utils.register_class(FTB_OT_Toggle_Face_Orient_Op)
    bpy.utils.register_class(FTB_OT_SelectScaleNonOne_Op)
    bpy.utils.register_class(FTB_OT_SelectScaleNonUniform_Op)
    bpy.utils.register_class(FTB_OT_SetToCenter_Op)
    bpy.utils.register_class(FTB_OT_OriginToCursor_Op)
    bpy.utils.register_class(FTB_OT_CheckNgons_Op)
    bpy.utils.register_class(FTB_OT_CopyLocation_Op)
    bpy.utils.register_class(FTB_OT_CopyRotation_Op)
    bpy.utils.register_class(FTB_OT_CopyScale_Op)
    bpy.utils.register_class(FTB_OT_ValidateMatSlots_Op)


def unregister():
    bpy.utils.unregister_class(FTB_OT_ValidateMatSlots_Op)
    bpy.utils.unregister_class(FTB_OT_Toggle_Face_Orient_Op)
    bpy.utils.unregister_class(FTB_OT_SelectScaleNonOne_Op)
    bpy.utils.unregister_class(FTB_OT_SelectScaleNonUniform_Op)
    bpy.utils.unregister_class(FTB_OT_SetToCenter_Op)
    bpy.utils.unregister_class(FTB_OT_OriginToCursor_Op)
    bpy.utils.unregister_class(FTB_OT_CheckNgons_Op)
    bpy.utils.unregister_class(FTB_OT_CopyLocation_Op)
    bpy.utils.unregister_class(FTB_OT_CopyRotation_Op)
    bpy.utils.unregister_class(FTB_OT_CopyScale_Op)
