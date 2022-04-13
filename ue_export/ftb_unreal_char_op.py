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


def register():
    bpy.utils.register_class(FTB_OT_UE_Char_Cleanup_Op)
    bpy.utils.register_class(FTB_OT_UE_Char_WeightParent_Op)


def unregister():
    bpy.utils.unregister_class(FTB_OT_UE_Char_WeightParent_Op)
    bpy.utils.unregister_class(FTB_OT_UE_Char_Cleanup_Op)
