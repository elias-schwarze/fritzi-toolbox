from urllib import robotparser
import bpy
from bpy.types import Operator


class FTB_OT_SetRootFromCursor(Operator):
    bl_idname = "object.set_root_from_cursor"
    bl_label = "Root from Cursor"
    bl_description = "Set root bone position from 3D Cursor"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.context.window_manager.ftbRootLoc = bpy.context.scene.cursor.location
        return {'FINISHED'}


class FTB_OT_SetHandleFromCursor(Operator):
    bl_idname = "object.set_handle_from_cursor"
    bl_label = "Handle from Cursor"
    bl_description = "Set handle bone position from 3D Cursor"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.context.window_manager.ftbHandleLoc = bpy.context.scene.cursor.location
        return {'FINISHED'}


class FTB_OT_CreateRigidRig_Op(Operator):
    bl_idname = "object.create_rigid_rig"
    bl_label = "Create Rig"
    bl_description = "Create a simple rig for rigid assets"
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
        childEmpty = context.object

        handleLoc = bpy.context.window_manager.ftbHandleLoc
        rootLoc = bpy.context.window_manager.ftbRootLoc

        # set up Armature Object and relevant data
        propRigData = bpy.data.armatures.new("FTB_PropArmature")
        edit_bones = propRigData.edit_bones
        propRigObj = bpy.data.objects.new("FTB_PropRig", propRigData)
        bpy.context.scene.collection.objects.link(propRigObj)

        # switch to edit mode so that editing edit_bones becomes possible
        bpy.context.view_layer.objects.active = propRigObj
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        rootBone = edit_bones.new(name="root")
        rootBone.head = rootLoc
        rootBone.tail = (rootLoc[0], rootLoc[1], rootLoc[2] + 1)

        handleBone = edit_bones.new(name="handle")
        handleBone.head = handleLoc
        handleBone.tail = (handleLoc[0], handleLoc[1], handleLoc[2] + 1)

        handleBone.parent = rootBone

        # switch to object mode to finalize changes to edit_bones
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        if childEmpty:
            childEmpty.parent = propRigObj
            childEmpty.parent_type = 'BONE'
            childEmpty.parent_bone = "handle"
            childEmpty.matrix_parent_inverse = handleBone.matrix.inverted()

        return {'FINISHED'}


def register():
    bpy.utils.register_class(FTB_OT_CreateRigidRig_Op)
    bpy.utils.register_class(FTB_OT_SetRootFromCursor)
    bpy.utils.register_class(FTB_OT_SetHandleFromCursor)


def unregister():
    bpy.utils.unregister_class(FTB_OT_SetHandleFromCursor)
    bpy.utils.unregister_class(FTB_OT_SetRootFromCursor)
    bpy.utils.unregister_class(FTB_OT_CreateRigidRig_Op)
