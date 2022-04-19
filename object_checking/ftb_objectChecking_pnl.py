import bpy
import bpy.utils
from bpy.types import Panel

from .ftb_objectChecking_op import AssetChecker

def ObjectsString(ObjectCount):
    return ((" Object", " Objects")[ObjectCount > 1])



class FTB_PT_Checking_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Object Checking"
    bl_category = "FTB"

    bpy.types.WindowManager.bActiveCollectionOnly = bpy.props.BoolProperty(
        default=True)

    bpy.types.WindowManager.bIgnoreWithoutSlots = bpy.props.BoolProperty(
        default=False)

    bpy.types.WindowManager.PropCollectionOverride = bpy.props.PointerProperty(type = bpy.types.Collection)
    bpy.types.WindowManager.PropEmptyOverride = bpy.props.PointerProperty(type = bpy.types.Object)

    def draw(self, context):
        
        def DrawErrorButton(ErrorList, OperatorString, Label):
            if ErrorList:
                ErrorCount = len(ErrorList)
                col.label(text = Label)
                col.operator(OperatorString, text = str(ErrorCount) + ObjectsString(ErrorCount))
        
        layout = self.layout
        col = layout.column()
        col.operator("view.toggle_face_orient", text="Toggle Face Orientation")
        
        col.prop(context.window_manager, "PropCollectionOverride")
        col.prop(context.window_manager, "PropEmptyOverride")
        col.operator("utils.performassetcheck")
        
        if not AssetChecker.bFileInWorkspace:
            col.alert = True
            col.operator("wm.savefile", text="File saved outside workspace!")
            col.alert = False

        if not AssetChecker.bPropIDFileName:
            col.operator("wm.savefile", text="Invalid Prop ID filename!")
        
        if not AssetChecker.bProperFileName:
            col.operator("wm.savefile", text="Invalid letters in filename!")

        if not AssetChecker.PropCollection:
            col.label(text="Unable to find prop collection!")
        else:
            if not AssetChecker.bEqualFileCollectionName:
                col.label(text="File and collection name not equal!")
            if not AssetChecker.bPropIDCollectionName:
                col.label(text="Invalid Prop ID collection!")
            if not AssetChecker.bProperCollectionName:
                col.label(text="Invalid letters in collection!")

            if AssetChecker.PropEmpty:
                if not AssetChecker.bEqualCollectonEmptyName:
                    col.label(text="Empty and collection name not equal!")
                if not AssetChecker.bEqualFileEmptyName:
                    col.label(text="File and Empty name not equal!")
                if not AssetChecker.bPropIDEmptyName:
                    col.label(text="Invalid Prop ID empty!")
                if not AssetChecker.bProperEmptyName:
                    col.label(text="Invalid letters in empty!")

            DrawErrorButton(AssetChecker.RogueObjectErrors, "object.showrogues", "Invalid Objects in Collection!")
            DrawErrorButton(AssetChecker.SubDLevelErrors, "object.showsubderror", "SubD Level Errors!")
            DrawErrorButton(AssetChecker.MissingDisplacementErrors, "object.showdisplaceerror", "Displacement Errors!")
            DrawErrorButton(AssetChecker.ApplyScaleErrors, "object.showscaleerror", "Apply Scale Errors!")
            DrawErrorButton(AssetChecker.NGonErrors, "object.showngonerror", "NGon Errors!")
            DrawErrorButton(AssetChecker.MissingSlotErrors, "object.showmissingsloterror", "Missing Material Slots!")
            DrawErrorButton(AssetChecker.SlotLinkErrors, "object.showslotlinkerror", "Material Link Error!")
            DrawErrorButton(AssetChecker.UnusedSlotErrors, "object.showunusedsloterror", "Unusued Material Slot!")
            DrawErrorButton(AssetChecker.ParentingErrors, "object.showparentingerror", "Parenting Errors!")


        col.label(text="", icon='ERROR')
        col.label(text="", icon='CHECKMARK')

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
