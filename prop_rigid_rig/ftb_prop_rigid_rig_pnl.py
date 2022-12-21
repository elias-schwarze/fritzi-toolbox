import bpy
from bpy.types import Panel


class FTB_PT_PropRigging_Panel(Panel):
    bl_label = "Prop Rigging"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FTB"
    bl_options = {"DEFAULT_CLOSED"}

    bpy.types.WindowManager.ftbRootLoc = bpy.props.FloatVectorProperty(
        name="Root Position", description="The location of the root bone.", default=(0.0, 0.0, 0.0), subtype='TRANSLATION')

    bpy.types.WindowManager.ftbHandleLoc = bpy.props.FloatVectorProperty(
        name="Handle Position", description="The location of the handle bone.", default=(0.0, 0.0, 0.0), subtype='TRANSLATION')

    bpy.types.WindowManager.ftbPropRigName = bpy.props.StringProperty(
        default="", name="Name")

    bpy.types.WindowManager.ftbRigCustomShape = bpy.props.EnumProperty(
        name="Handle",
        description="Desired custom bone shape for handle bone.",
        items=[
            ('CUBE', "Cube", "Cube shape"),
            ('DIAMOND', "Diamond", "Basic octahedron shape"),
            ('SPHERE', "Sphere", "Sphere shape made out of 3 overlapping circles")
        ],
        default='CUBE'
    )
    bpy.types.WindowManager.ftbBoneRotationMode = bpy.props.EnumProperty(
        name="Mode",
        description="Set the rotation mode of all bones",
        items=[
            ('QUATERNION', "Quaternion", ""),
            ('XYZ', "XYZ Euler", "")
        ],
        default='XYZ'

    )

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.prop(bpy.context.window_manager, "ftbRootLoc")
        col.operator("object.set_root_from_cursor")

        col.separator()

        col.prop(bpy.context.window_manager, "ftbHandleLoc")
        col.operator("object.set_handle_from_cursor")

        col.separator()

        col.prop(bpy.context.window_manager, "ftbPropRigName")
        col.separator()

        col.prop(bpy.context.window_manager, "ftbRigCustomShape")
        col.prop(bpy.context.window_manager, "ftbBoneRotationMode")

        col.separator()
        col.operator("object.create_rigid_rig")


def register():
    bpy.utils.register_class(FTB_PT_PropRigging_Panel)


def unregister():
    bpy.utils.unregister_class(FTB_PT_PropRigging_Panel)
