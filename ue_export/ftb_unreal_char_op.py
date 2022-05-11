import bpy
from bpy.types import Operator


class FTB_OT_UE_Char_Cleanup_Op(Operator):
    bl_idname = "utils.ue_char_cleanup"
    bl_label = "Char Cleanup"
    bl_description = "Clears modifiers, shapekeys and vertex groups of all selected objects"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            bpy.context.view_layer.objects.active = obj

            if bpy.context.active_object.type == 'MESH':
                if bpy.context.object.data.shape_keys:
                    bpy.ops.object.shape_key_remove(all=True)

            if bpy.context.active_object.vertex_groups:
                bpy.ops.object.vertex_group_remove(all=True)
            for mod in obj.modifiers:
                obj.modifiers.remove(mod)

        return {'FINISHED'}


class FTB_OT_UE_Char_WeightParent_Op(Operator):
    bl_idname = "utils.ue_char_weight_parent"
    bl_label = "Weight Paint To Bone"
    bl_description = "Weight paints all vertices of all selected objects to active bone"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        for obj in bpy.context.selected_objects:
            group = obj.vertex_groups['spine.006']
            vertex_indices = []

            for v in obj.data.vertices:
                vertex_indices.append(v.index)
            group.add(vertex_indices, 1.0, 'REPLACE')

        return {'FINISHED'}

    
class FTB_OT_UE_Char_AddUnrealRig_Op(Operator):
    bl_idname = "utils.ue_char_add_rig"
    bl_label = "Add Unreal Rig"
    bl_description = "Adds a Humanoid Rigify-Rig without face bones, for easy rigging for Unreal Mocap"
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

        # add rigify human metarig 
        bpy.ops.object.armature_human_metarig_add()
        rig = bpy.context.active_object.data
        
        # switch to edit mode to modify edit_bones
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)


        for bone in rig.edit_bones:
            # delete layer 0 bones (face)
                rig.edit_bones.remove(bone)

        # new for each loop to avoid iterating over an already deleted bone, which would result in a missing reference
        for bone in rig.edit_bones:
            # delete heel pivot bones
            if bone.name in ["heel.02.L", "heel.02.R"]:
               rig.edit_bones.remove(bone) 

        # switch to object mode to finalize changes to edit_bones
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(FTB_OT_UE_Char_AddUnrealRig_Op)
    bpy.utils.register_class(FTB_OT_UE_Char_Cleanup_Op)
    bpy.utils.register_class(FTB_OT_UE_Char_WeightParent_Op)


def unregister():
    bpy.utils.unregister_class(FTB_OT_UE_Char_WeightParent_Op)
    bpy.utils.unregister_class(FTB_OT_UE_Char_Cleanup_Op)
    bpy.utils.unregister_class(FTB_OT_UE_Char_AddUnrealRig_Op)
