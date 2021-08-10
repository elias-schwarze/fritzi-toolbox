import bpy

from bpy.types import Operator

from .. utility_functions.ftb_transform_utils import ob_Copy_Vis_Loc
from .. utility_functions.ftb_transform_utils import ob_Copy_Vis_Rot
from .. utility_functions.ftb_transform_utils import ob_Copy_Vis_Sca
from .. utility_functions.ftb_string_utils import strip_End_Numbers


class FTB_OT_RemoveMaterials_Op(Operator):
    bl_idname = "object.remove_all_materials"
    bl_label = "Remove All Materials"
    bl_description = "Remove all Material slots from all selected Objects"
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
        for m in bpy.data.materials:
            bpy.data.materials.remove(m)

        self.report({'INFO'}, 'Removed all Materials')
        return {'FINISHED'}

    def invoke(self, context, event):
        return bpy.context.window_manager.invoke_confirm(self, event)


class FTB_OT_PurgeUnusedData_Op(Operator):
    bl_idname = "data.purge_unused"
    bl_label = "Purge Unused Data"
    bl_description = "Recursively remove all unused Datablocks from file"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.outliner.orphans_purge(
            do_local_ids=True, do_linked_ids=True, do_recursive=True)
        self.report({'INFO'}, 'Purged unused Data')
        return {'FINISHED'}

    def invoke(self, context, event):
        return bpy.context.window_manager.invoke_confirm(self, event)


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


def register():
    bpy.utils.register_class(FTB_OT_RemoveMaterials_Op)
    bpy.utils.register_class(FTB_OT_PurgeUnusedData_Op)
    bpy.utils.register_class(FTB_OT_OverrideRetainTransform_Op)
    bpy.utils.register_class(FTB_OT_CollectionNameToMaterial_Op)
    bpy.utils.register_class(FTB_OT_ObjectNameToMaterial_Op)


def unregister():
    bpy.utils.unregister_class(FTB_OT_CollectionNameToMaterial_Op)
    bpy.utils.unregister_class(FTB_OT_RemoveMaterials_Op)
    bpy.utils.unregister_class(FTB_OT_PurgeUnusedData_Op)
    bpy.utils.unregister_class(FTB_OT_OverrideRetainTransform_Op)
    bpy.utils.unregister_class(FTB_OT_ObjectNameToMaterial_Op)
