import bpy
import bpy.utils
from bpy.types import Panel


class FTB_PT_Checking_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Object Checking"
    bl_category = "FTB"

    bpy.types.WindowManager.bActiveCollectionOnly = bpy.props.BoolProperty(
        default=True)

    bpy.types.WindowManager.bIgnoreWithoutSlots = bpy.props.BoolProperty(
        default=False)

    def draw(self, context):

        layout = self.layout

        col = layout.column()
        col.operator("view.toggle_face_orient", text="Toggle Face Orientation")

        col = layout.column(align=True)
        col.label(text="Scale Checking")

        col.operator("object.select_scale_non_one")
        col.operator("object.select_scale_non_unform")

        col = layout.column(align=True)
        col.label(text="Origin")

        col.operator("object.center_object")
        col.operator("object.origin_to_cursor")

        col = layout.column()
        col.label(text="Mesh Checking")
        col.operator("object.check_ngons")

        col = layout.column()
        col.label(text="Material Slots")

        row = layout.row(align=True)
        row.operator("object.validate_mat_slots")
        row.prop(data=context.window_manager,
                 property="bActiveCollectionOnly", toggle=True, icon_only=True, icon='OUTLINER_COLLECTION')

        col = layout.column()
        col.prop(context.window_manager,
                 "bIgnoreWithoutSlots", text="Ignore Objects Without Slots")

        # row = layout.row(align=True)
        # row.prop(context.window_manager, "bEnableLeft",
        #          text="Left", toggle=True)
        # row.prop(context.window_manager, "bEnableRight",
        #          text="Right", toggle=True)


def register():
    bpy.utils.register_class(FTB_PT_Checking_Panel)


def unregister():
    bpy.utils.unregister_class(FTB_PT_Checking_Panel)
