import bpy

from bpy.types import Operator
from bpy.props import EnumProperty


class FTB_OT_AddDisplaceModifier_Op(Operator):
    bl_idname = "object.add_displace_modifier"
    bl_label = "Add Displace Modifier"
    bl_description = "Add a displace modifier to the selected objects"
    bl_options = {"REGISTER", "UNDO"}

    direction: EnumProperty(items=(('XYZ', 'RGB to XYZ', ''),
                                   ('X',   'X', ''),
                                   ('Y',   'Y', ''),
                                   ('Z', 'Z', '')),
                            default='XYZ',
                            description='Displacement direction',
                            )

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

            if self.direction == 'XYZ':
                dispModifier.direction = 'RGB_TO_XYZ'

            elif self.direction == 'X':
                dispModifier.direction = 'X'

            elif self.direction == 'Y':
                dispModifier.direction = 'Y'

            elif self.direction == 'Z':
                dispModifier.direction = 'Z'

            dispModifier.strength = 0.01

        return {'FINISHED'}


def register():
    bpy.utils.register_class(FTB_OT_AddDisplaceModifier_Op)


def unregister():
    bpy.utils.unregister_class(FTB_OT_AddDisplaceModifier_Op)
