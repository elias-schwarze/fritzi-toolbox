import bpy

from bpy.types import Operator


class FTB_OT_AddDisplaceModifier_Op(Operator):
    bl_idname = "object.add_displace_modifier"
    bl_label = "Add Displace Modifier"
    bl_description = "Add a displace modifier to the selected objects"
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

        for obj in bpy.context.selected_objects:
            dispModifier = obj.modifiers.new("FDisplace", 'DISPLACE')
        return {'FINISHED'}


def register():
    bpy.utils.register_class(FTB_OT_AddDisplaceModifier_Op)


def unregister():
    bpy.utils.unregister_class(FTB_OT_AddDisplaceModifier_Op)
