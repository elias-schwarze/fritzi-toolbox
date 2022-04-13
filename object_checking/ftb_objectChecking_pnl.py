import bpy
import bpy.utils
from bpy.types import Panel

from .ftb_objectChecking_op import AssetChecker


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
        col.operator("utils.performassetcheck")

        if AssetChecker.PropCollection:
            col.label(text="Prop Collection found", icon='ERROR')

        if AssetChecker.bFileInWorkspace:
            col.label(text="File in Workspace", icon='ERROR')
        
        if AssetChecker.bPropIDFileName:
            col.label(text="PropID in Filename", icon='ERROR')
        
        if AssetChecker.bProperFileName:
            col.label(text="Chars valid in Filename", icon='ERROR')
        
        if AssetChecker.PropCollection:
            if AssetChecker.bPropIDFileName:
                col.label(text="PropID in Collection", icon='ERROR')
            if AssetChecker.bProperCollectionName:
                col.label(text="Chars valid in Collection", icon='ERROR')

            if AssetChecker.PropEmpty:
                
                if AssetChecker.bEqualNaming:
                    col.label(text="Names are Equal")

                col.label(text=AssetChecker.PropEmpty.name_full)
                if AssetChecker.bPropIDEmptyName:
                    col.label(text="PropID in Empty", icon='ERROR')
                if AssetChecker.bProperEmptyName:
                    col.label(text="Chars valid in Empty", icon='ERROR')

            if AssetChecker.SubDLevelErrors:
                col.operator("object.showsubderror")

        # ######## OLD DRAW
        # layout = self.layout

        # col = layout.column()
        # col.operator("view.toggle_face_orient", text="Toggle Face Orientation")

        # col = layout.column(align=True)
        # col.label(text="Transform Checking")

        # col.operator("object.select_location_non_zero")

        # col.operator("object.select_rotation_non_zero")

        # col.operator("object.select_scale_non_one")
        # col.operator("object.select_scale_non_unform")

        # col = layout.column(align=True)
        # col.label(text="Origin")

        # col.operator("object.center_object")
        # col.operator("object.origin_to_cursor")

        # col = layout.column(align=True)
        # col.label(text="Mesh Checking")
        # col.operator("object.check_ngons").showPolys = False
        # col.operator("object.check_ngons",
        #              text="Check and Show Ngons").showPolys = True

        # col = layout.column()
        # col.label(text="Orphan Data:")

        # col = layout.column()
        # col.operator("object.find_orphaned_objects")

        # col = layout.column()
        # col.operator("image.find_orphan_textures")

        # col = layout.column()
        # col.label(text="Material Slots")

        # row = layout.row(align=True)
        # row.operator("object.validate_mat_slots")
        # row.prop(data=context.window_manager,
        #          property="bActiveCollectionOnly", toggle=True, icon_only=True, icon='OUTLINER_COLLECTION')

        # col = layout.column()
        # col.prop(context.window_manager,
        #          "bIgnoreWithoutSlots", text="Ignore Objects Without Slots")


def register():
    bpy.utils.register_class(FTB_PT_Checking_Panel)


def unregister():
    bpy.utils.unregister_class(FTB_PT_Checking_Panel)
