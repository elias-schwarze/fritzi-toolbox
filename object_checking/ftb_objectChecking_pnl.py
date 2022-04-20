from importlib import import_module
import bpy
import bpy.utils
from bpy.types import Panel

from .ftb_objectChecking_op import AssetChecker
from .ftb_objectChecking_op import FTB_OT_PerformAssetCheck_Op

AC = AssetChecker

def PluralizeString(ObjectCount):
    return (("", "s")[ObjectCount > 1])

class FTB_PT_Checking_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Object Checking"
    bl_category = "FTB"

    bpy.types.WindowManager.bActiveCollectionOnly = bpy.props.BoolProperty(
        default=True)

    bpy.types.WindowManager.bIgnoreWithoutSlots = bpy.props.BoolProperty(
        default=False)

    bpy.types.WindowManager.PropCollectionOverride = bpy.props.PointerProperty(name= "", type = bpy.types.Collection)
    bpy.types.WindowManager.PropEmptyOverride = bpy.props.PointerProperty(name = "", type = bpy.types.Object)

    def draw(self, context):
        
        def DrawErrorButton(ErrorList, OperatorString, Label):
            if ErrorList:
                ErrorCount = len(ErrorList)
                col.operator(OperatorString, text = str(ErrorCount) + " - " + Label + PluralizeString(ErrorCount))
        
        _bFileError = not(AC.bFileInWorkspace and AC.bPropIDFileName and AC.bProperFileName and AC.bFileIsClean)
        _bCollectionError = not(AC.PropCollection and AC.bEqualFileCollectionName and 
                                AC.bProperCollectionName and AC.bPropIDCollectionName)
        _bEmptyError = not(AC.PropEmpty and AC.bEmptyOnWorldOrigin and AC.bEqualFileEmptyName and 
                            AC.bEqualCollectonEmptyName and AC.bPropIDEmptyName and AC.bProperEmptyName)
        _bObjectError = AC.RogueObjectErrors or AC.SubDLevelErrors or AC.MissingDisplacementErrors or \
                        AC.ApplyScaleErrors or AC.NGonErrors or AC.MissingSlotErrors or \
                        AC.SlotLinkErrors or AC.UnusedSlotErrors or AC.ParentingErrors

        layout = self.layout
        col = layout.column()
        col.operator("view.toggle_face_orient", text="Toggle Face Orientation")
        
        col.operator("utils.detectpropemptycollection")
        col.prop(context.window_manager, "PropCollectionOverride")
        col.prop(context.window_manager, "PropEmptyOverride")
        col.operator("utils.performassetcheck")
        
        if not context.window_manager.PropCollectionOverride or not context.window_manager.PropEmptyOverride or not FTB_OT_PerformAssetCheck_Op.Checker:
            return

        if _bFileError:
            col.separator(factor = 2)
            col.label(text = "File Errors", icon = 'FILE')

            if not AC.bFileInWorkspace:
                col.alert = True
                col.operator("wm.savefile", text="File saved outside workspace!")
                col.alert = False

            if not AC.bPropIDFileName:
                col.operator("wm.savefile", text="Filename - Invalid Prop ID!")
            
            if not AC.bProperFileName:
                col.operator("wm.savefile", text="Filename - Invalid letters!")
            
            if not AC.bFileInWorkspace:
                col.label(text = "File unclean!")

        
        if _bCollectionError:
            col.separator(factor = 2)
            col.label(text = "Collection Errors", icon = 'OUTLINER_COLLECTION')

        if not AC.PropCollection:
            col.label(text="Unable to find prop collection!")
        else:
            if not AC.bEqualFileCollectionName:
                col.operator("utils.changecollectionname", text="Name - Not Equal to Filename!")
            if not AC.bPropIDCollectionName:
                col.operator("utils.changecollectionname", text="Name - Invalid Prop ID!")
            if not AC.bProperCollectionName:
                col.operator("utils.changecollectionname", text="Name - Invalid letters!")

            if _bEmptyError:
                col.separator(factor = 2)
                col.label(text = "Empty Errors", icon = 'OUTLINER_OB_EMPTY')

                if not AC.bEqualCollectonEmptyName:
                    col.label(text="Name - Not Equal to Collection!")
                if not AC.bEqualFileEmptyName:
                    col.label(text="Name - Not Equal to Filename!")
                if not AC.bPropIDEmptyName:
                    col.label(text="Name - Invalid Prop ID!")
                if not AC.bProperEmptyName:
                    col.label(text="Name - Invalid letters!")
                if not AC.bEmptyOnWorldOrigin:
                    col.label(text="Not on World Origin!")

            if _bObjectError:
                col.separator(factor = 2)
                col.label(text = "Object Errors", icon = 'OUTLINER_OB_MESH')

                DrawErrorButton(AC.RogueObjectErrors, "object.showrogues", "Invalid Object")
                DrawErrorButton(AC.SubDLevelErrors, "object.showsubderror", "SubD Level Error")
                DrawErrorButton(AC.MissingDisplacementErrors, "object.showdisplaceerror", "Displacement Error")
                DrawErrorButton(AC.ApplyScaleErrors, "object.showscaleerror", "Apply Scale Error")
                DrawErrorButton(AC.NGonErrors, "object.showngonerror", "NGon Error")
                DrawErrorButton(AC.MissingSlotErrors, "object.showmissingsloterror", "Missing Material Slot")
                DrawErrorButton(AC.SlotLinkErrors, "object.showslotlinkerror", "Material Link Error")
                DrawErrorButton(AC.UnusedSlotErrors, "object.showunusedsloterror", "Unusued Material Slot")
                DrawErrorButton(AC.ParentingErrors, "object.showparentingerror", "Parenting Error")


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

